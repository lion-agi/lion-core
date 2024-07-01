# lion_core/abc/tao.py

from abc import ABC, abstractmethod
from typing import Any


class Abstraction(ABC):
    """
    The fundamental concept of existence in the LION system.
    Represents the most basic notion of 'being' or 'existing'.
    """


class MeasurableSpace(Abstraction):
    """
    Represents a Borel Space: the existence of a set and a σ(sigma)-field.
    Provides a foundation for defining measurable functions and probability measures.
    """


class Observable(Abstraction):
    """
    Represents a point with temporal attributes knowable to an external party.
    Forms the basis for elements that can be observed or measured.
    """


class Observer(Abstraction):
    """
    Represents a temporal snapshot state of a space.
    Encapsulates the entity or system doing the observing.
    """


class AbstractElement(Observable):
    """
    Represents an object measurable in time.
    Serves as a base class for concrete elements in the system.
    """


class AbstractCondition(Abstraction):
    """
    Represents a state of a space.
    Used to define specific configurations or properties of a space.
    """

    @abstractmethod
    async def applies(self, *args, **kwargs) -> bool:
        """
        Determines if the condition applies in the given context.
        """


class AbstractEvent(Abstraction):
    """
    Represents a change in a space.
    Encapsulates the concept of transitions or occurrences within the system.
    """
