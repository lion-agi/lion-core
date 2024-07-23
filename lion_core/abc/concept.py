"""
Core abstract base classes for Lion framework, integrating Taoism, Category
Theory, and Complex Systems Theory.
"""

from abc import ABC


class Tao(ABC):
    """
    Foundational abstraction embodying interconnectedness and existence.
    Root for all classes, reflecting Taoist unity and Category Theory relations.
    """


class AbstractSpace(Tao):
    """
    Abstract space or context, aligning with Category Theory's categories.
    Defines domain for elements and interactions, supporting system emergence.
    Subclasses implement __contains__ for membership criteria.
    """


class AbstractElement(Tao):
    """
    Observable entity within a space, reflecting Taoist individuality in unity.
    Embodies Category Theory objects and Complex Systems components.
    Capable of emergent behaviors through interactions.
    """

    @classmethod
    def class_name(cls) -> str:
        """Get class name, supporting reflection and metaprogramming."""
        return cls.__name__


class AbstractObserver(Tao):
    """
    Entity capable of observations, inspired by quantum mechanics and cognition.
    Prepresents intentionality and observer effect in complex systems.
    Subclasses implement specific observation mechanisms.
    """


class AbstractObservation(Tao):
    """
    Act of observing, integrating phenomenology and information theory.
    Captures information exchange and meaning construction in complex systems.
    """


# File: lion_core/abc/concept.py
