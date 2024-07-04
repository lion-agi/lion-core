# lion_core/abc/quantum.py

"""
LionAGI: Quantum Abstractions

This module defines abstract classes representing quantum concepts
in the LionAGI framework. These classes extend the AbstractCharacteristic
base class.
"""

from .tao import AbstractCharacteristic


class Quantum(AbstractCharacteristic):
    """Entities with quantum properties."""


class Superposable(Quantum):
    """Quantum entities that can be in superposition."""


class Entangleable(Quantum):
    """Quantum entities that can be entangled."""
