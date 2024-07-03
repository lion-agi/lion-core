"""Probabilistic abstractions for the Lion framework.

This module defines fundamental abstract classes that represent core
probabilistic and quantum concepts in the Lion framework. These abstractions
build upon the base AbstractCharacteristic class and provide a foundation for
modeling systems with uncertain, deterministic, or quantum properties.

Classes:
    Probabilistic: Entities with probabilistic behavior.
    Deterministic: Entities with deterministic behavior.
    Quantum: Entities with quantum properties.
    Superposable: Quantum entities that can be in superposition.
    Entangleable: Quantum entities that can be entangled.
"""

from .tao import AbstractCharacteristic


class Probabilistic(AbstractCharacteristic):
    """Represents entities with probabilistic behavior.

    This class forms the base for all elements in the Lion framework
    that involve uncertainty or randomness.
    """


class Deterministic(Probabilistic):
    """Represents entities with deterministic behavior.

    A special case of Probabilistic where outcomes are certain.
    This class is useful for modeling systems with predictable behavior.
    """


class Quantum(Probabilistic):
    """Represents entities with quantum properties.

    Base class for quantum elements, inheriting probabilistic nature.
    This class provides a foundation for modeling quantum systems.
    """


class Superposable(Quantum):
    """Represents quantum entities that can be in superposition.

    Applicable to quantum elements that can exist in multiple states
    simultaneously. This class is crucial for modeling quantum superposition.
    """


class Entangleable(Quantum):
    """Represents quantum entities that can be entangled.

    Used for quantum elements that can form non-local correlations.
    This class is essential for modeling quantum entanglement phenomena.
    """
    
    
# lion_core/abc/probabilistic.py