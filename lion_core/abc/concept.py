"""Core abstract base classes for the Lion framework."""

from abc import ABC


class Tao(ABC):
    """
    The foundational abstraction in the Lion framework, representing existence.

    This abstract base class serves as the root for all other classes in the
    framework, embodying the concept of Tao or fundamental existence.
    """


class AbstractSpace(Tao):
    """
    An abstract representation of a space or region.

    This class defines the concept of a space that can contain elements.
    Subclasses should implement the __contains__ method to define
    membership criteria for the space.
    """


class AbstractElement(Tao):
    """
    An abstract representation of an observable entity within a space.

    This class defines the concept of an element that can exist within
    an AbstractSpace. Subclasses should implement specific properties
    and behaviors of elements.
    """

    @classmethod
    def class_name(cls) -> str:
        """Get the name of the class."""
        return cls.__name__


class AbstractObserver(Tao):
    """
    An abstract representation of an entity capable of making observations.

    This class defines the concept of an observer that can perceive or
    interact with AbstractElements within an AbstractSpace. Subclasses
    should implement specific observation mechanisms.
    """


class AbstractObservation(Tao):
    """
    An abstract representation of the act of observing.
    """


# File: lion_core/abc/concept.py
