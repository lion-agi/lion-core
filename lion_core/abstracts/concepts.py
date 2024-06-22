from abc import ABC


class Element(ABC):
    """An observable part of a space."""
    pass

class Ordering(ABC):
    """A sequence of elements differing by comparison."""
    pass

class Event(ABC):
    """A change in state of an element."""
    pass

class Operation(ABC):
    """An ordering of events."""
    pass

class Operable(ABC):
    ...


class Condition(ABC):
    """A place in space where an operation is performed."""
    pass

class Container(ABC):
    """A structure containing elements."""
    pass

class Operator(ABC):
    """An element that carries out operations."""
    pass

class Record(ABC):
    """Persistence of elements across changes in space."""
    pass

class Relatable(Element):
    """Entities that can be described together in a meaningful way."""
    pass

class Sendable(Element):
    """An element that can be transferred among elements."""
    pass
