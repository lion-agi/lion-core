"""Conceptual abstractions for the Lion framework.

This module defines fundamental abstract classes that represent core
conceptual characteristics in the Lion framework. These abstractions
build upon the base Abstraction classes and provide a foundation for
modeling complex systems with time-dependent, observable, and operable
properties.

Classes:
    Temporal: Entities with time-dependent properties.
    Observable: Points with knowable temporal attributes.
    Operable: Entities that can be manipulated or acted upon.
    Relatable: Entities that can form relationships.
    Sendable: Entities that can be transmitted or communicated.
    Decidable: Entities that can be evaluated or determined.
"""

from abc import abstractmethod
from .tao import AbstractCharacteristic


class Temporal(AbstractCharacteristic):
    """Represents entities with time-dependent properties.

    This class forms the basis for all elements in the Lion framework
    that evolve or change over time.
    """


class Observable(Temporal):
    """Represents a point with temporal attributes knowable to an external party.

    This class extends Temporal to include the concept of observability,
    forming the basis for elements that can be observed or measured.
    """

    @abstractmethod
    def to_dict(self, *args, **kwargs): ...


class Operable(Observable):
    """Represents entities that can be manipulated or acted upon.

    This class is useful for elements that can be controlled or modified
    within the system.
    """

class Actionable(Operable):
    """Represents entities that can be acted upon or executed.

    This class is useful for elements that can be executed or triggered
    within the system.
    """


class Relatable(Operable):
    """Represents entities that can form relationships with other entities.

    This class enables modeling of interconnections and dependencies
    between elements in the system.
    """


class Sendable(Operable):
    """Represents entities that can be transmitted or communicated.

    This class is applicable to elements involved in information transfer
    or signaling within the system.
    """


class Decidable(Operable):
    """Represents entities that can be evaluated or determined.

    This class is useful for elements involved in decision-making or
    logical operations within the system.
    """

class Record(Operable):
    """Represents entities that can be recorded or stored.

    This class is useful for elements that can be stored or logged
    within the system.
    """
    
class Ordering(Operable):
    """Represents entities that can be ordered or sequenced.

    This class is useful for elements that can be arranged or ordered
    within the system.
    """
    
# lion_core/abc/concepts.py