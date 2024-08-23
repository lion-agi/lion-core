from abc import abstractmethod
from typing import Any

from lion_core.abc._concept import AbstractObservation


class Event(AbstractObservation):
    """
    Represents discrete occurrences or state changes in the system.

    This class serves as a base for more specific event types.
    """


class Condition(Event):
    """
    Represents state evaluation in complex systems.

    This class defines a condition that can be checked or applied.
    """

    @abstractmethod
    async def apply(self, *args: Any, **kwargs: Any) -> Any:
        """
        Apply the condition asynchronously.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Any: The result of applying the condition.
        """
        pass


class Signal(Event):
    """
    Represents a triggerable signal in the system.

    This class defines a signal that can be triggered.
    """

    @abstractmethod
    async def trigger(self, *args: Any, **kwargs: Any) -> Any:
        """
        Trigger the signal asynchronously.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Any: The result of triggering the signal.
        """
        pass


class Action(Event):
    """
    Represents an invokable action in the system.

    This class defines an action that can be invoked. Actions must have a
    status.
    """

    @abstractmethod
    async def invoke(self, *args: Any, **kwargs: Any) -> Any:
        """
        Invoke the action asynchronously.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Any: The result of invoking the action.
        """
        pass


__all__ = ["Event", "Condition", "Signal", "Action"]


# File: lion_core/abc/_observation.py
