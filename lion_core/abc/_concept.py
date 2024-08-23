from abc import ABC


class Tao(ABC):
    """
    Foundational abstraction embodying interconnectedness and existence.
    Root for all classes, reflecting Taoist unity and Category Theory relations
    """


class AbstractSpace(Tao):
    """Abstract space or context"""


class AbstractElement(Tao):
    """entity within a space"""

    @classmethod
    def class_name(cls) -> str:
        """Get class name, supporting reflection and metaprogramming."""
        return cls.__name__


class AbstractObserver(Tao):
    """Entity capable of observations, inspired by quantum mechanics"""


class AbstractObservation(Tao):
    """
    Act of observing, integrating phenomenology and information theory.
    Captures information exchange and meaning construction in complex systems.
    """


__all__ = [
    "AbstractSpace",
    "AbstractElement",
    "AbstractObserver",
    "AbstractObservation",
]


# File: lion_core/abc/concept.py
