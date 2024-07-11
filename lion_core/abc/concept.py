"""Core abstract base classes for the Lion framework."""

from abc import ABC, abstractmethod


class Node(ABC):
    """
    aka Tao, the foundation abstraction in the Lion framework. 
    Represents existence. 
    """
    
class AbstractSpace(Node):
    """An abstract expanse or region."""

    @abstractmethod
    def __contains__(self, item) -> bool: ...


class AbstractElement(Node):
    """An abstract observable entity in a space."""

    # @abstractmethod
    # def convert_to(self, new_type: type | str = "dict", **kwargs) -> Any: ...
    #
    # @classmethod
    # @abstractmethod
    # def convert_from(cls, data, new_type: type | str = "dict", **kwargs) -> Any: ...


class AbstractObserver(Node):
    """An abstract entity capable of making observations."""


# File: lion_core/abc/concept.py
