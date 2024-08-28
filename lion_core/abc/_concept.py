from abc import ABC, abstractmethod


class Tao(ABC):
    """the lion way"""


class AbstractSpace(Tao):
    """Abstract space or context."""

    @abstractmethod
    def __contains__(self, item: object) -> bool:
        """Check if an item is in the space."""


class AbstractElement(Tao):
    """Entity within a space."""

    @classmethod
    def class_name(cls) -> str:
        """
        Get class name.

        Returns:
            str: The name of the class.
        """
        return cls.__name__


# must have async abstract methods
class AbstractObserver(Tao):
    """Entity capable of making observations"""


# must have async abstract methods
class AbstractObservation(Tao):
    """Act of observing."""


__all__ = [
    "AbstractSpace",
    "AbstractElement",
    "AbstractObserver",
    "AbstractObservation",
]


# File: lion_core/abc/_concept.py
