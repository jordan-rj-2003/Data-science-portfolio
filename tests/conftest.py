"""Shared fixtures for the sanity-check test suite (spec 001 task 10).

The GloVe model is loaded once per test session (session-scoped) since
loading it is slow (~90s) — every test that needs real vectors shares the
same cached instance via src.glove.get_model()'s own module-level cache.
"""

from pathlib import Path

import pytest

from src.glove import get_model

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
ARTICLE_IDS = [f"A{i}" for i in range(1, 12)]


@pytest.fixture(scope="session")
def glove_model():
    return get_model()
