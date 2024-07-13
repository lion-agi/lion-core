"""
Abstract space classes for the Lion framework.

This module defines container-like structures that extend the concept of
AbstractSpace, incorporating principles from measure theory, complex systems,
and quantum-inspired computation to model multi-faceted, dynamic entities.
"""

from abc import abstractmethod
from typing import Any, TypeVar, Generic, Optional

from .concept import AbstractSpace

T = TypeVar("T")


class Container(AbstractSpace):
    """
    A container that is both an element and an abstract space.

    This class extends AbstractSpace to represent collections of elements,
    drawing inspiration from measure theory and category theory. It provides
    a foundation for modeling complex systems where the whole (container)
    and its parts (elements) are treated uniformly, allowing for recursive
    structures and emergent behaviors.
    """


class Ordering(Container):
    """
    A container with a defined order.

    This class extends Container to include concepts from order theory,
    providing a foundation for sequences, priority queues, and other
    structures where the relative positions of elements are significant.
    """
    @abstractmethod
    def __len__(self) -> int:
        """
        Return the number of items in the container.

        This method relates to the concept of cardinality in set theory,
        providing a measure of the container's size.
        """

    @abstractmethod
    def size(self) -> int:
        """
        Return the size of the container.

        Similar to numpy.size(), this method may account for multi-dimensional
        or nested structures, reflecting the complexity of the container.
        """

    @abstractmethod
    def is_empty(self) -> bool:
        """
        Check if the container is empty.

        This method is crucial for boundary conditions in algorithms and
        relates to the concept of null sets in measure theory.
        """

    @abstractmethod
    def clear(self) -> None:
        """
        Remove all items from the container.

        This operation resets the container to its initial state, which
        is important for reusability and state management in complex systems.
        """

    @abstractmethod
    def copy(self) -> "Container":
        """
        Return a shallow copy of the container.

        This method is crucial for creating independent instances, which
        is important in parallel processing and state preservation.
        """

    @abstractmethod
    def append(self, *args, **kwargs) -> None:
        """
        Add an item to the end of the container.

        This method allows for dynamic growth of the container, reflecting
        the adaptability of complex systems.
        """

    @abstractmethod
    def pop(self, *args, **kwargs) -> Any:
        """
        Remove and return item at index (default last).

        This method combines removal and retrieval, which is useful for
        stack-like operations and priority queues.
        """

    @abstractmethod
    def include(self, item: T) -> bool:
        """
        Include an item if not already present.

        This method ensures uniqueness within the container, which can be
        crucial for set-like operations and maintaining invariants.
        """

    @abstractmethod
    def exclude(self, item: T) -> bool:
        """
        Exclude an item if present.

        This method allows for selective removal, which is important for
        filtering and maintaining specific conditions within the container.
        """

    @abstractmethod
    def __getitem__(self, index: int) -> Any:
        """
        Get item at index.

        This method provides direct access to elements, which is fundamental
        for array-like operations and random access patterns.
        """

    @abstractmethod
    def __setitem__(self, index: int, item: Any) -> None:
        """
        Set item at index.

        This method allows for in-place modifications, which can be more
        efficient than removal and reinsertion in certain scenarios.
        """

    @abstractmethod
    def __delitem__(self, index: int) -> None:
        """
        Delete item at index.

        This method provides fine-grained control over the container's
        contents, allowing for selective removal of elements.
        """

    @abstractmethod
    def __iter__(self) -> Any:
        """
        Return an iterator for the container.

        This method enables the use of the container in for loops and
        comprehensions, facilitating data processing and transformations.
        """

    @abstractmethod
    def __next__(self) -> Any:
        """
        Return the next item in the container.

        This method works with __iter__ to enable iteration, which is
        crucial for sequential processing of container elements.
        """

    @abstractmethod
    def __list__(self) -> list:
        """
        Return the container as a list.

        This method provides a standard Python representation of the
        container, which can be useful for interoperability and serialization.
        """

    @abstractmethod
    def keys(self) -> Any:
        """
        Return the keys of the container.

        This method is crucial for associative containers and can represent
        indices in ordered containers, facilitating lookup operations.
        """

    @abstractmethod
    def values(self) -> Any:
        """
        Return the values of the container.

        This method provides access to the core data stored in the container,
        which is essential for data processing and analysis tasks.
        """

    @abstractmethod
    def items(self) -> Any:
        """
        Return the items of the container as (key, value) pairs.

        This method combines keys and values, which is useful for
        simultaneous access to both in iterations and transformations.
        """

    @abstractmethod
    def __reverse__(self) -> "Ordering":
        """
        Return a reversed copy of the ordering.

        This operation is crucial for algorithms that process data in
        reverse order and for implementing bi-directional iterations.
        """

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        """
        Check if two orderings are equal.

        This method defines equality for ordered containers, which may
        consider both element values and their relative positions.
        """

    @abstractmethod
    def index(self, item: Any, start: int = 0, end: Optional[int] = None) -> int:
        """
        Return first index of item. Raise ValueError if not found.

        This method is essential for search operations and can be used
        to implement more complex algorithms like binary search.
        """

    @abstractmethod
    def remove(self, item: Any) -> None:
        """
        Remove the first occurrence of an item.

        This method combines search and removal operations, which is
        useful for maintaining ordered collections without duplicates.
        """

    @abstractmethod
    def popleft(self) -> Any:
        """
        Remove and return the first item.

        This method is crucial for implementing queue-like behaviors
        and can be used in breadth-first search algorithms.
        """

    @abstractmethod
    def extend(self, *args, **kwargs) -> None:
        """
        Add multiple items to the end of the ordering.

        This method allows for bulk insertion operations, which can be
        more efficient than multiple individual append operations.
        """

    @abstractmethod
    def count(self, *args, **kwargs) -> int:
        """
        Return number of occurrences of item.

        This method is useful for frequency analysis and can be used
        in statistical operations on the container's contents.
        """


class Index(Ordering):
    """
    An index structure based on Ordering.

    This class specializes Ordering to represent index structures,
    which are crucial in database-like operations, fast lookups,
    and maintaining relationships between different data sets.
    """


class Collective(Container, Generic[T]):
    """
    A record-like structure in the Lion framework.

    This class combines aspects of containers and associative structures,
    providing a foundation for modeling complex, multi-faceted entities.
    It incorporates ideas from category theory and type theory to allow
    for flexible, type-safe implementations of record-like structures.
    """
    
    @abstractmethod
    def __len__(self) -> int:
        """
        Return the number of items in the container.

        This method relates to the concept of cardinality in set theory,
        providing a measure of the container's size.
        """

    @abstractmethod
    def size(self) -> int:
        """
        Return the size of the container.

        Similar to numpy.size(), this method may account for multi-dimensional
        or nested structures, reflecting the complexity of the container.
        """

    @abstractmethod
    def is_empty(self) -> bool:
        """
        Check if the container is empty.

        This method is crucial for boundary conditions in algorithms and
        relates to the concept of null sets in measure theory.
        """

    @abstractmethod
    def clear(self) -> None:
        """
        Remove all items from the container.

        This operation resets the container to its initial state, which
        is important for reusability and state management in complex systems.
        """

    @abstractmethod
    def copy(self) -> "Container":
        """
        Return a shallow copy of the container.

        This method is crucial for creating independent instances, which
        is important in parallel processing and state preservation.
        """

    @abstractmethod
    def append(self, *args, **kwargs) -> None:
        """
        Add an item to the end of the container.

        This method allows for dynamic growth of the container, reflecting
        the adaptability of complex systems.
        """

    @abstractmethod
    def pop(self, *args, **kwargs) -> Any:
        """
        Remove and return item at index (default last).

        This method combines removal and retrieval, which is useful for
        stack-like operations and priority queues.
        """

    @abstractmethod
    def include(self, item: T) -> bool:
        """
        Include an item if not already present.

        This method ensures uniqueness within the container, which can be
        crucial for set-like operations and maintaining invariants.
        """

    @abstractmethod
    def exclude(self, item: T) -> bool:
        """
        Exclude an item if present.

        This method allows for selective removal, which is important for
        filtering and maintaining specific conditions within the container.
        """

    @abstractmethod
    def __getitem__(self, index: int) -> Any:
        """
        Get item at index.

        This method provides direct access to elements, which is fundamental
        for array-like operations and random access patterns.
        """

    @abstractmethod
    def __setitem__(self, index: int, item: Any) -> None:
        """
        Set item at index.

        This method allows for in-place modifications, which can be more
        efficient than removal and reinsertion in certain scenarios.
        """

    @abstractmethod
    def __delitem__(self, index: int) -> None:
        """
        Delete item at index.

        This method provides fine-grained control over the container's
        contents, allowing for selective removal of elements.
        """

    @abstractmethod
    def __iter__(self) -> Any:
        """
        Return an iterator for the container.

        This method enables the use of the container in for loops and
        comprehensions, facilitating data processing and transformations.
        """

    @abstractmethod
    def __next__(self) -> Any:
        """
        Return the next item in the container.

        This method works with __iter__ to enable iteration, which is
        crucial for sequential processing of container elements.
        """

    @abstractmethod
    def __list__(self) -> list:
        """
        Return the container as a list.

        This method provides a standard Python representation of the
        container, which can be useful for interoperability and serialization.
        """

    @abstractmethod
    def keys(self) -> Any:
        """
        Return the keys of the container.

        This method is crucial for associative containers and can represent
        indices in ordered containers, facilitating lookup operations.
        """

    @abstractmethod
    def values(self) -> Any:
        """
        Return the values of the container.

        This method provides access to the core data stored in the container,
        which is essential for data processing and analysis tasks.
        """

    @abstractmethod
    def items(self) -> Any:
        """
        Return the items of the container as (key, value) pairs.

        This method combines keys and values, which is useful for
        simultaneous access to both in iterations and transformations.
        """

    @abstractmethod
    def update(self, other: Any) -> None:
        """
        Update with items from another record or iterable.

        This method allows for bulk updates and merging of data, which
        is crucial for maintaining consistency across related data sets
        and implementing synchronization mechanisms.
        """

    @abstractmethod
    def get(self, key: Any, default: Any = None) -> T:
        """
        Return item at key if present, else default.

        This method provides a safe way to access elements, incorporating
        the concept of optional types or Maybe monads from functional
        programming to handle potential absence of values.
        """


# File: lion_core/abc/container.py
