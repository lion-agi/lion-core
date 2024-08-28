from lion_core.abc._concept import Tao


class Characteristic(Tao):
    """Base class for Lion framework characteristics."""


class Observable(Characteristic):
    """Identifiable objects with a 'ln_id' attribute."""

    ln_id: str


class Temporal(Characteristic):
    """objects existing in time with a 'timestamp' attribute."""

    timestamp: float


class Communicatable(Observable, Temporal):
    """Represents entities that can be used for communication."""

    sender: str
    recipient: str


class Quantum(Characteristic):
    """quantum-inspired approaches for modeling of non-classical behaviors."""


class Probabilistic(Characteristic):
    """entities with inherent uncertainty."""


class Stochastic(Probabilistic, Temporal):
    """Combines probabilistic and time-dependent aspects."""


class Relational(Observable):
    """only relational entities can be nodes in a graph"""


class Traversal(Observable):
    """progressable or explorable entities"""


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
