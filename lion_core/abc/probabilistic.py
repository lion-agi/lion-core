# lion_core/abc/probabilistic.py

"""
LionAGI: Probabilistic Abstractions

This module defines abstract classes representing probabilistic concepts
in the LionAGI framework. These classes extend the AbstractCharacteristic
base class.
"""

from .tao import AbstractCharacteristic


class Probabilistic(AbstractCharacteristic):
    """Entities with probabilistic behavior."""


class Deterministic(Probabilistic):
    """Entities with deterministic behavior (certain outcomes)."""


class Stochastic(Probabilistic):
    """Entities with random, time-evolving behavior."""
