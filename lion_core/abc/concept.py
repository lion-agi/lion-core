"""Core abstract base classes for the Lion framework."""

from abc import ABC, abstractmethod


class Node(ABC):
    """
    The foundational abstraction in the Lion framework, representing existence.

    This abstract base class serves as the root for all other classes in the
    framework, embodying the concept of Tao or fundamental existence.
    """


class AbstractSpace(Node):
    """
    An abstract representation of a space or region.

    This class defines the concept of a space that can contain elements.
    Subclasses should implement the __contains__ method to define
    membership criteria for the space.
    """

    @abstractmethod
    def __contains__(self, item) -> bool:
        """
        Check if an item is contained within this space.

        Args:
            item: The item to check for containment.

        Returns:
            bool: True if the item is in the space, False otherwise.
        """


class AbstractElement(Node):
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


class AbstractObserver(Node):
    """
    An abstract representation of an entity capable of making observations.

    This class defines the concept of an observer that can perceive or
    interact with AbstractElements within an AbstractSpace. Subclasses
    should implement specific observation mechanisms.
    """


# File: lion_core/abc/concept.py
