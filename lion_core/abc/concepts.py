from typing import Generator
from abc import ABC, abstractmethod


## nouns
class Element(ABC):
    """represents a part of a space"""

    @abstractmethod
    def to_dict(self, *args, **kwargs) -> dict: ...


class Ordering(ABC):
    """represents a structure of elements in a space"""

    @abstractmethod
    def __next__(self): ...


class Container(ABC):
    """represents a group of elements"""

    @abstractmethod
    def __contains__(self, item): ...

    @abstractmethod
    def size(self) -> list | tuple | int: ...

    @abstractmethod
    def values(self) -> Generator:
        """Return an iterator over items in the record."""

    @abstractmethod
    def get(self, a): ...

    @abstractmethod
    def __getitem__(
        self,
        a,
    ): ...

    @abstractmethod
    def __setitem__(self, a, b): ...


class Event(ABC):
    """represents a change in a space"""

    @abstractmethod
    async def set(self): ...


class Condition(ABC):
    """represents a state of a space"""

    @abstractmethod
    async def applies(self, *args, **kwargs): ...


class Temporal(Element):
    """an element that can be referenced in time"""

    def __bool__(self):
        return True


class Record(Element):
    """a collection of elements"""

    @abstractmethod
    def get(self, a): ...

    @abstractmethod
    def keys(self): ...


## adjectives
class Decidable(Element): ...


class Operable(Element): ...


class Relatable(Element):

    @abstractmethod
    def relate(self, *arg, **kwargs): ...


class Sendable(Element): ...
