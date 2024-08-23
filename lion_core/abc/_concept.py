from abc import ABC


class Tao(ABC):
    """
    Foundational abstraction embodying existence.

    This class serves as the base for all abstract concepts in the system.
    """


class AbstractSpace(Tao):
    """
    Abstract space or context.

    Represents a conceptual space or context within the system.
    """


class AbstractElement(Tao):
    """
    Entity within a space.

    Represents an abstract element that can exist within an AbstractSpace.
    """

    @classmethod
    def class_name(cls) -> str:
        """
        Get class name, supporting reflection and metaprogramming.

        Returns:
            str: The name of the class.
        """
        return cls.__name__


class AbstractObserver(Tao):
    """
    Entity capable of observations, inspired by quantum mechanics.

    Represents an abstract observer that can make observations in the system.
    """


class AbstractObservation(Tao):
    """
    Act of observing.

    Represents the abstract concept of an observation made by an
    AbstractObserver.
    """


__all__ = [
    "AbstractSpace",
    "AbstractElement",
    "AbstractObserver",
    "AbstractObservation",
]


# File: lion_core/abc/_concept.py
