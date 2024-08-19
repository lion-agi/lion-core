"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from abc import abstractmethod
from lion_core.abc._concept import AbstractObservation
from lion_core.abc._characteristic import Observable


class Event(AbstractObservation):
    """
    Base class for LION events. Represents discrete occurrences or state
    changes in complex systems. Inspired by event-driven architectures and
    quantum state transitions, models deterministic and probabilistic processes.
    """

    pass


class Condition(Event):
    """
    Represents a checkable condition in LION. Embodies state evaluation
    in complex systems, analogous to quantum observables. Checking may
    influence system state, aligning with quantum measurement theory.
    """

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
