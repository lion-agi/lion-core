from abc import ABC, abstractmethod
from typing import Any


class Tao(ABC):
    """A way to existence"""

    pass


class AbstractSpace(Tao):
    """An abstract expanse or region."""

    pass


class AbstractElement(Tao):
    """An abstract observable entity in a space."""

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Convert the element to a dictionary representation."""
        pass


class AbstractObserver(Tao):
    """An abstract entity capable of making observations."""

    pass


class AbstractObservation(Tao):
    """An abstract snapshot of states of a space."""

    pass


class AbstractEvent(Tao):
    """An abstract change in space state."""

    pass


class Characteristic(ABC):
    """Base class for characteristics."""

    pass


class Observable(Characteristic):
    """Characteristic of being observable."""

    pass


class Temporal(Characteristic):
    """Characteristic of having a temporal aspect."""

    pass


class Quantum(Characteristic):
    """Characteristic of having quantum properties."""

    pass


class Probabilistic(Characteristic):
    """Characteristic of being probabilistic."""

    pass


# File: lion_core/abc/concept.py
