"""Edge module for the Lion framework.

This module defines the Edge class for representing edges in graph structures
within the Lion framework. It extends the Relation class to provide specific
functionality for edge representation and manipulation.

Classes:
    Edge: Represents a directed or undirected edge between two nodes.
"""

from typing import Any

from pydantic import Field, field_validator

from ..primitive.util import get_lion_id
from .relation import Relation


class Edge(Relation):
    """Represents a directed or undirected edge between two nodes in a graph.

    This class extends the Relation class to represent edges in a graph,
    providing methods for validation and basic operations. Edge properties
    can be stored and retrieved using the metadata field inherited from the
    Component class.

    Attributes:
        head (str): The identifier of the head node of the edge.
        tail (str): The identifier of the tail node of the edge.
    """

    head: str = Field(..., description="The identifier of the head node of the edge.")
    tail: str = Field(..., description="The identifier of the tail node of the edge.")

    @field_validator("head", "tail", mode="before")
    @classmethod
    def validate_node_id(cls, value: Any) -> str:
        """Validate and convert node identifiers.

        Args:
            value (Any): The value to be validated and converted.

        Returns:
            str: The validated and converted node identifier.
        """
        return get_lion_id(value)

    def __contains__(self, item: Any) -> bool:
        """Check if the given item is the head or tail of the edge.

        Args:
            item (Any): The item to check.

        Returns:
            bool: True if the item is the head or tail of the edge,
                  False otherwise.
        """
        return get_lion_id(item) in (self.head, self.tail)

    def __len__(self) -> int:
        """Return the number of nodes in the edge (always 2).

        Returns:
            int: The number of nodes in the edge (always 2).
        """
        return 2

    def __str__(self) -> str:
        """Return a concise string representation of the Edge.

        Returns:
            str: A string representation of the Edge.
        """
        return (
            f"Edge(head={self.head[:8]}..., tail={self.tail[:8]}..., "
            f"weight={self._meta_get('weight', 1.0):.2f}, directed={self.directed})"
        )

    def __repr__(self) -> str:
        """Return a detailed string representation of the Edge.

        Returns:
            str: A detailed string representation of the Edge.
        """
        return (
            f"Edge(ln_id={self.ln_id}, head={self.head}, tail={self.tail}, "
            f"weight={self._meta_get('weight', 1.0)}, directed={self.directed}, "
            f"label={self.label!r}, condition={self.condition!r}, "
            f"metadata={self.metadata}, content={self.content!r})"
        )


# Path: lion_core/generic/edge.py
