from abc import abstractmethod

from lion_core.abc._concept import AbstractObservation


class Event(AbstractObservation):
    """discrete occurrences or state changes"""


class Condition(Event):
    """Represents state evaluation in complex systems,"""

    @abstractmethod
    async def apply(self, *args, **kwargs):
        pass


class Signal(Event):
    """a triggerable signal"""

    @abstractmethod
    async def trigger(self, *args, **kwargs):
        pass


class Action(Event):
    """Represents an invokable action"""

    # action must have status

    @abstractmethod
    async def invoke(self, *args, **kwargs):
        pass


__all__ = ["Event", "Condition", "Signal", "Action"]


# File: lion_core/abc/observation.py
