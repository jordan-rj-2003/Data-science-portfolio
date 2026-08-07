"""Zone-boundary spot checks, spec 001 task 10.

Covers: normal path on all 11 real articles, the minimum-paragraph
boundary case, and the too-short failure mode.
"""

import pytest

from src.segmentation import (
    ArticleTooShortError,
    ZONE_LABELS,
    load_article,
    segment,
    segment_corpus,
)
from tests.conftest import ARTICLE_IDS, RAW_DIR


@pytest.mark.parametrize("article_id", ARTICLE_IDS)
def test_zones_reconstruct_from_paragraphs_with_no_overlap(article_id):
    """Each zone is built from the expected paragraph slice, and the lead
    paragraph (Z1) never shares a paragraph index with the end zone (Z3) —
    the non-overlap the minimum-3-paragraph constraint exists to guarantee."""
    header, paragraphs = load_article(RAW_DIR / f"{article_id}.txt")
    zones = segment(header, paragraphs)

    lead = paragraphs[0]
    end = paragraphs[-2:]
    body = paragraphs[1:-2]

    assert zones[1] == f"{header} {lead}"
    assert zones[2] == " ".join(body)
    assert zones[3] == " ".join(end)
    assert zones[4] == " ".join([header] + paragraphs)

    # Index-level non-overlap: the lead is paragraph 0, the end is the
    # last two paragraphs; with >= 3 paragraphs these can never collide.
    end_start_index = len(paragraphs) - 2
    assert end_start_index >= 1, "lead (index 0) would overlap the end zone"


def test_zone_labels_match_spec():
    assert ZONE_LABELS == {1: "Headline+Lead", 2: "Body", 3: "End", 4: "Whole"}


def test_three_paragraph_article_has_empty_body_and_no_overlap():
    """Boundary case: the minimum allowed length (exactly 3 paragraphs)
    must still produce a valid, non-overlapping Z1/Z3 split, with Z2 empty."""
    header = "Headline"
    paragraphs = ["Lead paragraph.", "Second to last.", "Last paragraph."]
    zones = segment(header, paragraphs)
    assert zones[2] == ""  # body is empty — nothing between lead and end
    assert zones[1] == "Headline Lead paragraph."
    assert zones[3] == "Second to last. Last paragraph."


def test_article_below_minimum_paragraphs_raises(tmp_path):
    short_article = tmp_path / "short.txt"
    short_article.write_text("Headline\n\nOnly paragraph one.\n\nOnly paragraph two.\n")
    with pytest.raises(ArticleTooShortError):
        load_article(short_article)


def test_segment_corpus_produces_44_uniquely_identified_pieces():
    pieces = segment_corpus(RAW_DIR, ARTICLE_IDS)
    assert len(pieces) == 44
    assert len(set(pieces)) == 44  # no duplicate IDs
    for article_id in ARTICLE_IDS:
        for zone_num in range(1, 5):
            assert f"{article_id}Z{zone_num}" in pieces
