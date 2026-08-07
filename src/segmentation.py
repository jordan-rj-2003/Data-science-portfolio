"""Zone segmentation per spec 001 WHAT §2.

File format (data/raw/A{n}.txt): line 1 is the header (headline, with a
" — " separated deck/subtitle folded in where the outlet had one — see
journal 2026-07-18 for why decks are folded into the header rather than
left as a separate paragraph block), then a blank line, then body
paragraphs separated by blank lines.

Zones:
  Z1 Headline+Lead = header + first real paragraph
  Z2 Body           = paragraphs between the lead and the last two
  Z3 End            = last two paragraphs
  Z4 Whole          = header + every real paragraph

Minimum 3 real paragraphs required (spec 001 Constraints) so Z1 and Z3
never overlap.
"""

from pathlib import Path

ZONE_LABELS = {1: "Headline+Lead", 2: "Body", 3: "End", 4: "Whole"}


class ArticleTooShortError(ValueError):
    pass


def load_article(path):
    content = Path(path).read_text(encoding="utf-8").strip()
    blocks = [b.strip() for b in content.split("\n\n") if b.strip()]
    header, paragraphs = blocks[0], blocks[1:]
    if len(paragraphs) < 3:
        raise ArticleTooShortError(
            f"{path} has only {len(paragraphs)} real paragraphs; "
            "minimum 3 required (spec 001 Constraints)."
        )
    return header, paragraphs


def segment(header, paragraphs):
    """Return {zone_num: text} for one article's four zones."""
    lead = paragraphs[0]
    end = paragraphs[-2:]
    body = paragraphs[1:-2]  # may be empty
    return {
        1: f"{header} {lead}",
        2: " ".join(body),
        3: " ".join(end),
        4: " ".join([header] + paragraphs),
    }


def segment_article(path):
    header, paragraphs = load_article(path)
    return segment(header, paragraphs)


def segment_corpus(raw_dir, article_ids):
    """Return {"A{n}Z{z}": text} for every article/zone combination."""
    pieces = {}
    for article_id in article_ids:
        path = Path(raw_dir) / f"{article_id}.txt"
        zones = segment_article(path)
        for zone_num, text in zones.items():
            pieces[f"{article_id}Z{zone_num}"] = text
    return pieces
