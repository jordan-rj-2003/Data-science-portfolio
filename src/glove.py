"""Shared GloVe model loader — reuses the same model already used in
notebooks/MSC PROJECT.ipynb (glove-wiki-gigaword-300), per spec 001
Constraints ("must reuse the existing GloVe model... this phase does not
re-derive the axis"). Loaded once and cached.
"""

import gensim.downloader as api

_MODEL = None


def get_model():
    global _MODEL
    if _MODEL is None:
        _MODEL = api.load("glove-wiki-gigaword-300")
    return _MODEL
