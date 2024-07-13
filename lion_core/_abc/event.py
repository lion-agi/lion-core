"""Abstract event classes for the Lion framework."""

from abc import abstractmethod
from .concept import AbstractElement


class Event(AbstractElement):
    """Base class for concrete events."""

    pass


class Condition(Event):
    """An event representing a condition to be checked."""

    @abstractmethod
    async def apply(self, *args, **kwargs):
        """Apply the condition."""
        pass


class Signal(Event):
    """An event representing a signal to be triggered."""

    @abstractmethod
    async def trigger(self, *args, **kwargs):
        """Trigger the signal."""
        pass


class Action(Event):
    """An event representing an action to be invoked."""

    @abstractmethod
    async def invoke(self, *args, **kwargs):
        """Invoke the action."""
        pass


# File: lion_core/abc/event.py
