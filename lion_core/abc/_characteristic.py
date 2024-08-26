from lion_core.abc._concept import Tao


class Characteristic(Tao):
    """
    Base class for Lion framework characteristics.

    Represents fundamental properties of Nodes, inspired by property dualism.
    Forms building blocks for modeling complex systems and emergent behaviors.
    """


class Observable(Characteristic):
    """Defines observable entities.

    Rooted in quantum measurement theory, represents elements perceivable
    by AbstractObserver. Must have an 'ln_id' attribute.
    """

    ln_id: str


class Temporal(Characteristic):
    """
    Represents time-evolving properties or behaviors.

    Inspired by dynamical systems theory, essential for modeling
    time-dependent processes and state changes in complex systems. Must
    have a 'timestamp' attribute.
    """

    timestamp: float


class Communicatable(Observable, Temporal):
    """Represents entities that can be communicated."""

    sender: str
    recipient: str


class Quantum(Characteristic):
    """
    Embodies quantum concepts like superposition and entanglement.

    Enables modeling of non-classical behaviors in cognitive and
    computational processes, key to quantum-inspired approaches.
    """


class Probabilistic(Characteristic):
    """
    Represents entities with inherent uncertainty.

    Grounded in probability theory and stochastic processes, crucial for
    modeling decision-making and multi-outcome systems.
    """


class Stochastic(Probabilistic, Temporal):
    """
    Combines probabilistic and time-dependent aspects.

    Integrates stochastic processes and time series analysis for modeling
    systems with evolving randomness, like financial markets or biological
    processes.
    """


class Relational(Observable):
    """
    Represents inherently connected or related entities.

    Fundamental for modeling networked systems, social interactions, and
    complex relationships across various domains.
    """


class Traversal(Observable):
    """
    Represents traversable or explorable entities.

    Inspired by graph theory and network science, essential for modeling
    paths, connections, and information flow in complex networked systems.
    """


__all__ = [
    "Observable",
    "Temporal",
    "Relational",
    "Traversal",
    "Communicatable",
    # "Quantum",
    # "Probabilistic",
    # "Stochastic",
]

# File: lion_core/abc/_characteristic.py
