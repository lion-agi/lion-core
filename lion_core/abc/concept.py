"""Core abstract base classes for the Lion framework."""

from abc import ABC, abstractmethod
from typing import Any


class AbstractSpace(ABC):
    """An abstract expanse or region."""

    @abstractmethod
    def __contains__(self, item) -> bool: ...


class AbstractElement(ABC):
    """An abstract observable entity in a space."""

    # @abstractmethod
    # def convert_to(self, new_type: type | str = "dict", **kwargs) -> Any: ...
    #
    # @classmethod
    # @abstractmethod
    # def convert_from(cls, data, new_type: type | str = "dict", **kwargs) -> Any: ...


class AbstractObserver(ABC):
    """An abstract entity capable of making observations."""


# File: lion_core/abc/concept.py
