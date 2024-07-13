from abc import ABC


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


# File: lion_core/abc/characteristic.py
