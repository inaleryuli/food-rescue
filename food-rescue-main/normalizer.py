"""Compatibility import; maintained implementation: src.normalizer."""
from src.normalizer import *
from src import normalizer as _implementation


def __getattr__(name):
    return getattr(_implementation, name)
