"""Characteristic classes for the Lion framework."""

from .concept import Tao


class Characteristic(Tao):
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

    # must have ln_id

    pass


class Temporal(Characteristic):
    """
    Characteristic of having a temporal aspect.

    Inspired by dynamical systems theory, this characteristic represents
    properties or behaviors that evolve over time. It's fundamental to
    modeling time-dependent processes and state changes in complex systems.
    """

    # must have timestamp

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


class Relational(Observable):
    """
    Characteristic of having relational properties.

    Represents entities that are inherently connected or related to
    other entities. This characteristic is fundamental to modeling
    networked systems, social interactions, and complex relationships
    in various domains.
    """

    pass


class Traversal(Observable):
    """
    Characteristic of being traversable.

    Inspired by graph theory and network science, this characteristic
    represents entities that can be traversed or explored. It's
    essential for modeling paths, connections, and information flow
    in complex systems with a network structure.
    """

    pass


# File: lion_core/abc/characteristic.py
