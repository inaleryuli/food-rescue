"""Compatibility import; maintained implementation: src.engine."""
from src.engine import *
from src import engine as _implementation


def __getattr__(name):
    return getattr(_implementation, name)

if __name__ == "__main__":
    from src.app import main
    main()
