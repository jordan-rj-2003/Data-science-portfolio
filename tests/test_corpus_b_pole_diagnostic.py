"""Tests for src/corpus_b_pole_diagnostic.py."""

from src.corpus_b_pole_diagnostic import average_by_group, group_by_pole_lean, sum_by_group


def test_group_by_pole_lean_buckets_correctly():
    summary = {
        "E1": {"n_survivors": 5, "n_balanced": 4, "n_unbalanced": 1},   # diff +3
        "E2": {"n_survivors": 5, "n_balanced": 1, "n_unbalanced": 3},   # diff -2
        "E3": {"n_survivors": 4, "n_balanced": 2, "n_unbalanced": 2},   # diff 0
    }
    groups = group_by_pole_lean(summary)
    assert groups["positive_pole"] == {"E1": 3}
    assert groups["negative_pole"] == {"E2": -2}
    assert groups["tied"] == {"E3": 0}


def test_sum_by_group_sums_diffs_within_each_bucket():
    summary = {
        "E1": {"n_survivors": 5, "n_balanced": 5, "n_unbalanced": 4},   # diff +1
        "E2": {"n_survivors": 5, "n_balanced": 4, "n_unbalanced": 5},   # diff -1
        "E3": {"n_survivors": 6, "n_balanced": 5, "n_unbalanced": 7},   # diff -2
        "E4": {"n_survivors": 6, "n_balanced": 8, "n_unbalanced": 4},   # diff +4
    }
    groups = group_by_pole_lean(summary)
    sums = sum_by_group(groups)
    assert sums["positive_pole"] == 1 + 4
    assert sums["negative_pole"] == -1 + -2
    assert sums["tied"] == 0


def test_sum_by_group_handles_empty_bucket():
    summary = {"E1": {"n_survivors": 3, "n_balanced": 3, "n_unbalanced": 1}}
    groups = group_by_pole_lean(summary)
    sums = sum_by_group(groups)
    assert sums["negative_pole"] == 0
    assert sums["tied"] == 0
    assert sums["positive_pole"] == 2


def test_average_by_group_computes_mean_diff_per_bucket():
    summary = {
        "E1": {"n_survivors": 5, "n_balanced": 5, "n_unbalanced": 4},   # diff +1
        "E2": {"n_survivors": 6, "n_balanced": 8, "n_unbalanced": 4},   # diff +4
        "E3": {"n_survivors": 5, "n_balanced": 4, "n_unbalanced": 5},   # diff -1
        "E4": {"n_survivors": 6, "n_balanced": 5, "n_unbalanced": 7},   # diff -2
    }
    groups = group_by_pole_lean(summary)
    averages = average_by_group(groups)
    assert averages["positive_pole"] == (1 + 4) / 2
    assert averages["negative_pole"] == (-1 + -2) / 2


def test_average_by_group_handles_empty_bucket_without_division_error():
    summary = {"E1": {"n_survivors": 3, "n_balanced": 3, "n_unbalanced": 1}}
    groups = group_by_pole_lean(summary)
    averages = average_by_group(groups)
    assert averages["negative_pole"] == 0.0
    assert averages["tied"] == 0.0
    assert averages["positive_pole"] == 2.0


def test_all_pieces_accounted_for_across_buckets():
    summary = {
        "E1": {"n_survivors": 5, "n_balanced": 4, "n_unbalanced": 1},
        "E2": {"n_survivors": 5, "n_balanced": 1, "n_unbalanced": 3},
        "E3": {"n_survivors": 4, "n_balanced": 2, "n_unbalanced": 2},
    }
    groups = group_by_pole_lean(summary)
    all_pieces = set(groups["positive_pole"]) | set(groups["negative_pole"]) | set(groups["tied"])
    assert all_pieces == set(summary.keys())
