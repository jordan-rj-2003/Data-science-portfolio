"""Tests for src/token_pole_diagnostic.py."""

from src.axis import build_balance_axis
from src.token_pole_diagnostic import compute_token_diagnostics, summarize


def test_compute_token_diagnostics_sorted_by_weight_descending(glove_model):
    axis = build_balance_axis(glove_model)
    weights = {"A1Z4": {"anchored": 1.0, "shameful": 5.0, "capital": 2.0}}
    diagnostics = compute_token_diagnostics(glove_model, axis, weights)
    tokens = [t for t, _, _ in diagnostics["A1Z4"]]
    assert tokens == ["shameful", "capital", "anchored"]


def test_compute_token_diagnostics_returns_one_row_per_survivor(glove_model):
    axis = build_balance_axis(glove_model)
    weights = {"A1Z4": {"anchored": 1.0, "shameful": 5.0}, "A2Z4": {"facts": 3.0}}
    diagnostics = compute_token_diagnostics(glove_model, axis, weights)
    assert len(diagnostics["A1Z4"]) == 2
    assert len(diagnostics["A2Z4"]) == 1


def test_summarize_counts_poles_correctly(glove_model):
    axis = build_balance_axis(glove_model)
    # "shameful" is strongly negative (unbalanced), "anchored" strongly
    # positive (balanced) on the balance axis -- confirmed by hand in the
    # 2026-07-26 diagnostic session.
    weights = {"A1Z4": {"anchored": 1.0, "shameful": 1.0}}
    diagnostics = compute_token_diagnostics(glove_model, axis, weights)
    summary = summarize(diagnostics)
    assert summary["A1Z4"]["n_survivors"] == 2
    assert summary["A1Z4"]["n_balanced"] == 1
    assert summary["A1Z4"]["n_unbalanced"] == 1


def test_summarize_handles_empty_piece(glove_model):
    axis = build_balance_axis(glove_model)
    diagnostics = compute_token_diagnostics(glove_model, axis, {"A1Z4": {}})
    summary = summarize(diagnostics)
    assert summary["A1Z4"] == {"n_survivors": 0, "n_balanced": 0, "n_unbalanced": 0}
