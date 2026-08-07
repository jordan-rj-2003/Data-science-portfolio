"""TF-IDF weighting spot checks, spec 001 task 10.

Covers the two documented correction mechanisms (continuity correction at
df=N, high-TF cap) and the flat baseline, against small hand-constructed
corpora where the expected numbers can be checked by hand.
"""

import math

from src.tfidf import (
    HIGH_TF_IDF_CAP,
    HIGH_TF_THRESHOLD,
    compute_flat_weights,
    compute_idf,
    compute_idf_plain,
    compute_weights,
    compute_weights_plain,
    group_by_zone,
)


def test_group_by_zone_splits_by_trailing_zone_number():
    pieces = {"A1Z1": ["a"], "A1Z2": ["b"], "A2Z1": ["c"]}
    groups = group_by_zone(pieces)
    assert set(groups.keys()) == {1, 2}
    assert set(groups[1]) == {"A1Z1", "A2Z1"}
    assert set(groups[2]) == {"A1Z2"}


def test_continuity_correction_gives_small_nonzero_idf_at_df_equals_n():
    """A term in every document must not collapse to idf=0 (which would
    erase repetition signal); it must still sit below the df=N-1 value so
    ordering between "universal" and "almost-universal" terms is preserved."""
    n = 11
    zone_pieces = {f"A{i}Z1": ["universal"] for i in range(1, n + 1)}
    zone_pieces["A1Z1"] = ["universal", "almost_universal"]
    for i in range(2, n):  # A2..A10 also get almost_universal (df=9, not N)
        zone_pieces[f"A{i}Z1"].append("almost_universal")

    idf = compute_idf(zone_pieces)

    assert idf["universal"] > 0  # not exactly zero despite df == n
    expected_universal = math.log(n / (n - 0.5))
    assert idf["universal"] == expected_universal
    # ordering preserved: a term missing from just one doc is still rarer
    assert idf["universal"] < idf["almost_universal"]


def test_high_tf_cap_overrides_natural_idf_only_for_that_piece():
    """A term repeated >10 times in one piece gets its effective idf
    capped in that piece specifically, even though the same term keeps its
    natural (uncapped) idf wherever it doesn't exceed the threshold."""
    pieces = {
        "A1Z1": ["the"] * 15 + ["distinct"],
        "A2Z1": ["the"] * 3,
        "A3Z1": ["other"],
    }
    weights = compute_weights(pieces)

    natural_idf_the = compute_idf({"A1Z1": pieces["A1Z1"], "A2Z1": pieces["A2Z1"], "A3Z1": pieces["A3Z1"]})["the"]
    capped_weight = 15 * HIGH_TF_IDF_CAP
    assert weights["A1Z1"]["the"] == capped_weight
    assert weights["A1Z1"]["the"] != 15 * natural_idf_the

    # A2Z1's "the" (TF=3, below threshold) uses the natural idf, uncapped
    assert weights["A2Z1"]["the"] == 3 * natural_idf_the


def test_high_tf_threshold_boundary_is_exclusive():
    """TF exactly at the threshold must NOT be capped; only TF strictly
    greater than HIGH_TF_THRESHOLD is."""
    pieces = {
        "A1Z1": ["word"] * HIGH_TF_THRESHOLD,
        "A2Z1": ["other"],
    }
    weights = compute_weights(pieces)
    natural_idf = compute_idf(pieces)["word"]
    assert weights["A1Z1"]["word"] == HIGH_TF_THRESHOLD * natural_idf


def test_flat_weights_ignore_document_frequency_entirely():
    """compute_flat_weights must equal raw term frequency, with no idf
    factor — the ablation baseline against TF-IDF."""
    pieces = {"A1Z1": ["a", "a", "b"], "A2Z1": ["a"]}
    weights = compute_flat_weights(pieces)
    assert weights["A1Z1"] == {"a": 2, "b": 1}
    assert weights["A2Z1"] == {"a": 1}


def test_plain_idf_gives_exact_zero_at_df_equals_n():
    """Spec 002: compute_idf_plain must NOT apply the continuity
    correction — a term in every document gets idf=ln(N/N)=0 exactly,
    reproducing the pre-2026-07-18 behaviour on purpose, as the
    naive-baseline contrast against compute_idf()'s corrected version."""
    zone_pieces = {f"A{i}Z1": ["universal"] for i in range(1, 12)}
    idf = compute_idf_plain(zone_pieces)
    assert idf["universal"] == 0.0


def test_plain_idf_matches_corrected_idf_away_from_the_df_equals_n_boundary():
    """Away from the df=N boundary, compute_idf_plain and compute_idf
    should agree exactly — the continuity correction only ever touches
    the exact df=N case."""
    zone_pieces = {
        "A1Z1": ["rare"],
        "A2Z1": ["other"],
        "A3Z1": ["other"],
    }
    plain = compute_idf_plain(zone_pieces)
    corrected = compute_idf(zone_pieces)
    assert plain["rare"] == corrected["rare"]
    assert plain["other"] == corrected["other"]


def test_plain_weights_apply_no_high_tf_cap():
    """Spec 002: compute_weights_plain must NOT cap high-TF terms — a
    term repeated 50 times in one piece gets weight = 50 * its natural
    (uncapped, uncorrected) idf, unlike compute_weights()'s capped
    version."""
    pieces = {
        "A1Z1": ["the"] * 50,
        "A2Z1": ["the"] * 2,
        "A3Z1": ["other"],
    }
    weights = compute_weights_plain(pieces)
    natural_idf = compute_idf_plain(pieces)["the"]
    assert weights["A1Z1"]["the"] == 50 * natural_idf
    # confirm this is actually a large, uncapped weight, not the tiny
    # HIGH_TF_IDF_CAP-based value compute_weights() would have produced
    assert weights["A1Z1"]["the"] != 50 * HIGH_TF_IDF_CAP
