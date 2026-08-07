"""TF-IDF per zone-type, spec 001 WHAT §4.

Custom, unpadded IDF: idf(t) = ln(N/df(t)) — deliberately not
scikit-learn's TfidfVectorizer, which always adds +1 in both its smoothed
and non-smoothed modes and so can never produce a literal zero for a
term appearing in every document. N=11 per zone-type corpus (one piece
per article, four corpora: Z1 Headline+Lead, Z2 Body, Z3 End, Z4 Whole).
TF is raw count within the piece, no scaling.

Two combined corrections (2026-07-18), each fixing a different failure
mode of the plain formula:

1. **Continuity correction at df=N**: a term present in literally every
   document gets idf=ln(N/N)=0 under the plain formula, so weight=TF*0=0
   regardless of TF — erasing any distinction between a universal term
   used once vs. repeated several times (e.g. "responsible", from the
   widely-quoted WADA statement, used twice by one outlet, once
   elsewhere). Fixed by treating df=N as N-0.5 only at that exact
   boundary, giving a small nonzero idf that still sits below the real
   df=N-1 value, preserving ordering.
2. **High-TF cap**: applying (1) alone reopened a much bigger problem —
   stopwords and punctuation are near-guaranteed to be both universal
   *and* have very high within-document TF (a comma or "the" can appear
   40-50+ times in one Body), so even the small continuity-corrected idf
   gets amplified by that TF into a dominant weight (worst case observed:
   a hyphen outweighed the single most distinctive word in the corpus).
   Also, some offenders (e.g. that hyphen, appearing in 9 of 11 Bodies,
   not all 11) were never at the exact df=N boundary in the first place,
   so (1) alone wouldn't catch them regardless. Fixed by capping the
   *effective* idf at a small fixed constant for any term whose TF in a
   specific piece exceeds a threshold — overriding whatever idf would
   otherwise apply (continuity-corrected or not).

Together: low-TF terms (<=10 in a given piece, which covers ordinary
content-word repetition) use the continuity-corrected idf, so a universal
content word's repetition still counts. High-TF terms (>10, which in
practice only ever hits structural/function words in this corpus —
verified no genuinely rare word is ever repeated that often) get capped,
so they can't dominate through sheer repetition. Threshold/cap values
(TF>10 -> idf=0.0005) chosen so the cap stays well below the smallest
realistic nonzero weight a genuine content word carries naturally
(idf~=0.095 at df=10). This keeps punctuation and function words in play
rather than hard-zeroing them outright — consistent with the project's
principle of not assuming in advance that a token carries no signal
(spec 001 WHAT §3); GloVe has vectors for all of them (verified), so they
can still nudge the document vector's direction, just not dominate it.

weight(t, piece) = TF(t, piece) * IDF_effective(t, piece), where
IDF_effective is the capped constant if TF>10 in that piece, otherwise
the term's (continuity-corrected) idf(t) from its zone-type corpus.
"""

import math
from collections import Counter, defaultdict

HIGH_TF_THRESHOLD = 10
HIGH_TF_IDF_CAP = 0.0005


def group_by_zone(pieces):
    """pieces: {"A{n}Z{z}": [tokens]} -> {zone_num: {"A{n}Z{z}": [tokens]}}"""
    groups = defaultdict(dict)
    for piece_id, tokens in pieces.items():
        zone_num = int(piece_id.split("Z")[1])
        groups[zone_num][piece_id] = tokens
    return groups


def compute_idf(zone_pieces):
    """zone_pieces: {"A{n}Z{z}": [tokens]} for one zone-type (N documents).
    Returns {term: idf} using idf(t) = ln(N / df(t)), with a continuity
    correction only at the exact df=N boundary (treated as N-0.5) so a
    universal term gets a small nonzero idf instead of exactly zero.
    """
    n = len(zone_pieces)
    df = Counter()
    for tokens in zone_pieces.values():
        df.update(set(tokens))  # once per document, regardless of repeats
    idf = {}
    for term, freq in df.items():
        effective_df = freq - 0.5 if freq == n else freq
        idf[term] = math.log(n / effective_df)
    return idf


def compute_weights(pieces):
    """pieces: {"A{n}Z{z}": [tokens]} for all pieces across all zone-types.
    Returns {"A{n}Z{z}": {term: tf_idf_weight}} — per-piece term weights.
    idf is computed (continuity-corrected) within each piece's own
    zone-type corpus; any term whose TF exceeds HIGH_TF_THRESHOLD in a
    given piece has its effective idf capped at HIGH_TF_IDF_CAP for that
    piece specifically, regardless of its natural value.
    """
    zone_groups = group_by_zone(pieces)
    weights = {}
    for zone_pieces in zone_groups.values():
        idf = compute_idf(zone_pieces)
        for piece_id, tokens in zone_pieces.items():
            tf = Counter(tokens)
            piece_weights = {}
            for term, count in tf.items():
                effective_idf = HIGH_TF_IDF_CAP if count > HIGH_TF_THRESHOLD else idf[term]
                piece_weights[term] = count * effective_idf
            weights[piece_id] = piece_weights
    return weights


def compute_idf_plain(zone_pieces):
    """Spec 002: plain idf(t) = ln(N/df(t)), no continuity correction — a
    term present in every document of the zone-type corpus gets exactly
    idf=0, reproducing the pre-2026-07-18 erasure-of-repetition problem
    on purpose, as the naive-baseline comparison point."""
    n = len(zone_pieces)
    df = Counter()
    for tokens in zone_pieces.values():
        df.update(set(tokens))
    return {term: math.log(n / freq) for term, freq in df.items()}


def compute_weights_plain(pieces):
    """Spec 002: weight(t, piece) = TF(t, piece) * idf(t), plain idf, no
    high-TF cap — the naive-baseline weighting variant, contrasted against
    compute_weights()'s continuity correction + high-TF cap."""
    zone_groups = group_by_zone(pieces)
    weights = {}
    for zone_pieces in zone_groups.values():
        idf = compute_idf_plain(zone_pieces)
        for piece_id, tokens in zone_pieces.items():
            tf = Counter(tokens)
            weights[piece_id] = {term: count * idf[term] for term, count in tf.items()}
    return weights


def compute_flat_weights(pieces):
    """Baseline with no TF-IDF weighting at all — weight(t, piece) = TF(t,
    piece), i.e. the IDF factor is dropped entirely (not set to 1; simply
    not applied). Mathematically equivalent to a plain "flat" mean-pooled
    average over every token occurrence — the naive document-embedding
    approach Hanselowski et al. found "fell behind" LSI/BoW (cited in spec
    001 WHY), used here as the comparison baseline for whether TF-IDF
    weighting is actually adding anything over a flat average.

    pieces: {"A{n}Z{z}": [tokens]} for all pieces (zone grouping doesn't
    matter here since there's no corpus-level IDF to compute).
    """
    weights = {}
    for piece_id, tokens in pieces.items():
        weights[piece_id] = dict(Counter(tokens))
    return weights
