"""Tests for src/control_text_balance_axis_check.py, spec 010 task 5."""

from src.control_text_balance_axis_check import _range_str, _whole_zone_pieces


def test_whole_zone_pieces_only_returns_z4_pieces():
    pieces = _whole_zone_pieces()
    assert len(pieces) == 11
    assert all(pid.endswith("Z4") for pid in pieces)


def test_whole_zone_pieces_are_nonempty_text():
    pieces = _whole_zone_pieces()
    assert all(len(text) > 0 for text in pieces.values())


def test_range_str_reports_min_max_mean():
    result = _range_str({"a": 1.0, "b": 2.0, "c": 3.0})
    assert "min 1.0000" in result
    assert "max 3.0000" in result
    assert "mean 2.0000" in result


def test_range_str_handles_empty_scores():
    assert _range_str({}) == "no scores available"
