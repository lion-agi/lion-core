from abc import abstractmethod

from lion_core.abc._concept import AbstractObservation


class Event(AbstractObservation):
    """discrete occurrences or state changes"""


class Condition(Event):
    """Represents state evaluation in complex systems,"""

    @abstractmethod
    async def apply(self, *args, **kwargs):
        """
        Asynchronously evaluates the condition, potentially altering
        system state. Enables non-blocking operations for modeling parallel
        processes in complex and quantum-inspired systems.
        """
        pass


class Signal(Event):
    """
    Represents a triggerable signal in LION. Analogous to quantum state
    broadcasts or information propagation in complex networks. Facilitates
    inter-system communication, enabling emergent behaviors.
    """

    @abstractmethod
    async def trigger(self, *args, **kwargs):
        """
        Asynchronously triggers the signal, potentially causing cascading
        effects. Models concurrent signal propagation, mirroring quantum
        state evolution or information diffusion in complex networks.
        """
        pass


class Action(Event):
    """
    Represents an invokable action in LION. Embodies executable processes
    modifying system state. Analogous to quantum operators or state transition
    functions in complex adaptive systems.
    """

    # action must have status

    @abstractmethod
    async def invoke(self, *args, **kwargs):
        """
        Asynchronously executes the action, potentially transforming
        system state. Models concurrent operations and time-evolving
        processes, aligning with quantum and complex system dynamics.
        """
        pass


__all__ = ["Event", "Condition", "Signal", "Action"]


# File: lion_core/abc/observation.py
