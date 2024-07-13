"""Characteristic classes for the Lion framework."""

from abc import ABC


class Characteristic(ABC):
    """
    Base class for characteristics in the Lion framework.

    Represents fundamental properties that can be associated with Nodes,
    drawing inspiration from property dualism. These characteristics
    form the building blocks for modeling complex systems and their
    emergent behaviors.
    """

    pass


class Observable(Characteristic):
    """
    Characteristic of being observable.

    Rooted in quantum measurement theory, this characteristic defines
    entities that can be perceived or measured by an AbstractObserver.
    It plays a crucial role in LION's implementation of quantum-inspired
    computation and cognitive modeling.
    """

    pass


class Temporal(Characteristic):
    """
    Characteristic of having a temporal aspect.

    Inspired by dynamical systems theory, this characteristic represents
    properties or behaviors that evolve over time. It's fundamental to
    modeling time-dependent processes and state changes in complex systems.
    """

    pass


class Quantum(Characteristic):
    """
    Characteristic of having quantum properties.

    Embodies quantum mechanical concepts such as superposition and
    entanglement. This characteristic is key to LION's quantum-inspired
    approach, enabling the modeling of non-classical behaviors in
    cognitive and computational processes.
    """

    pass


class Probabilistic(Characteristic):
    """
    Characteristic of being probabilistic.

    Grounded in probability theory and stochastic processes, this
    characteristic represents entities with inherent uncertainty.
    It's essential for modeling decision-making processes and
    systems with multiple possible outcomes.
    """

    pass


class Stochastic(Probabilistic, Temporal):
    """
    Characteristic of being both probabilistic and time-dependent.

    Combines concepts from stochastic processes and time series analysis.
    This characteristic is crucial for modeling complex systems with
    randomness that evolves over time, such as financial markets or
    biological processes.
    """

    pass


# File: lion_core/abc/characteristic.py
