# lion_core/abc/concepts.py

from abc import ABC, abstractmethod
from typing import Any


class Characteristic(ABC):
    """
    Base class for all characteristics.
    Provides a common root for properties that can be applied to elements.
    """


class Temporal(Characteristic):
    """
    Represents entities with time-dependent properties.
    Applicable to elements that evolve or change over time.
    """


class Operable(Characteristic):
    """
    Represents entities that can be manipulated or acted upon.
    Useful for elements that can be controlled or modified.
    """


class Relatable(Characteristic):
    """
    Represents entities that can form relationships with other entities.
    Enables modeling of interconnections and dependencies between elements.
    """


class Sendable(Characteristic):
    """
    Represents entities that can be transmitted or communicated.
    Applicable to elements involved in information transfer or signaling.
    """


class Decidable(Characteristic):
    """
    Represents entities that can be evaluated or determined.
    Useful for elements involved in decision-making or logical operations.
    """


class Probabilistic(Characteristic):
    """
    Represents entities with probabilistic behavior.
    Base class for all elements involving uncertainty or randomness.
    """


class Deterministic(Probabilistic):
    """
    Represents entities with deterministic behavior.
    A special case of Probabilistic where outcomes are certain.
    """


class Quantum(Probabilistic):
    """
    Represents entities with quantum properties.
    Base class for quantum elements, inheriting probabilistic nature.
    """


class Superposable(Quantum):
    """
    Represents quantum entities that can be in superposition.
    Applicable to quantum elements that can exist in multiple states simultaneously.
    """


class Entangleable(Quantum):
    """
    Represents quantum entities that can be entangled.
    Used for quantum elements that can form non-local correlations.
    """


class ValueSpace(Characteristic):
    """
    Base class for characteristics related to the nature of values.
    Defines the type of values an entity can take.
    """


class Quantized(ValueSpace):
    """
    Represents entities with discrete, quantized values.
    Applicable to elements with distinct, separable states.
    """

    @abstractmethod
    def allowed_values(self) -> set[Any]:
        """
        Returns the set of allowed values for this quantized entity.
        """


class Continuous(ValueSpace):
    """
    Represents entities with continuous values.
    Used for elements with smoothly varying properties.
    """

    @abstractmethod
    def value_range(self) -> tuple[Any, Any]:
        """
        Returns the range of possible values for this continuous entity.
        """
