"""Core abstract base classes for the Lion framework."""

from abc import ABC


class AbstractSpace(ABC):
    """An abstract expanse or region."""


class AbstractElement(ABC):
    """An abstract observable entity in a space."""


class AbstractObserver(ABC):
    """An abstract entity capable of making observations."""


# File: lion_core/abc/concept.py
