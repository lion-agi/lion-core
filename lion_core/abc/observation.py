"""
Abstract event classes for the Lion framework.

This module defines event-based structures that extend the concept of
AbstractElement, incorporating principles from complex systems theory,
quantum mechanics, and asynchronous programming to model dynamic,
state-changing entities within the LION framework.
"""

from abc import abstractmethod
from .concept import AbstractObservation


class Event(AbstractObservation):
    """
    Base class for concrete events in the Lion framework.

    Events in LION represent discrete occurrences or state changes within
    a complex system. They draw inspiration from event-driven architectures
    and quantum state transitions, allowing for the modeling of both
    deterministic and probabilistic processes in cognitive and computational
    systems.
    """

    pass


class Condition(Event):
    """
    An event representing a condition to be checked.

    Conditions in LION embody the concept of state evaluation in complex
    systems. They can be likened to quantum observables, where the act of
    checking a condition may influence the system's state, aligning with
    principles of quantum measurement theory.
    """

    @abstractmethod
    async def apply(self, *args, **kwargs):
        """
        Apply the condition asynchronously.

        This method evaluates the condition, potentially altering the
        system's state. The asynchronous nature allows for non-blocking
        operations, crucial in modeling parallel processes in complex
        systems and quantum-inspired computations.
        """
        pass


class Signal(Event):
    """
    An event representing a signal to be triggered.

    Signals in LION are analogous to quantum state broadcasts or classical
    information propagation in complex networks. They facilitate
    communication between different parts of a system, enabling emergent
    behaviors and self-organization.
    """

    @abstractmethod
    async def trigger(self, *args, **kwargs):
        """
        Trigger the signal asynchronously.

        This method initiates the signal, potentially causing cascading
        effects throughout the system. The asynchronous design allows for
        modeling of concurrent signal propagation, similar to parallel
        quantum state evolution or information diffusion in complex networks.
        """
        pass


class Action(Event):
    """
    An event representing an action to be invoked.

    Actions in LION represent executable processes that can modify the
    system's state. They can be thought of as operators in quantum mechanics
    or as state transition functions in complex adaptive systems, embodying
    the dynamic and transformative aspects of the framework.
    """

    @abstractmethod
    async def invoke(self, *args, **kwargs):
        """
        Invoke the action asynchronously.

        This method executes the action, potentially transforming the
        system's state. The asynchronous nature allows for modeling of
        concurrent operations and time-evolving processes, aligning with
        both quantum time evolution and complex system dynamics.
        """
        pass


# File: lion_core/abc/event.py
