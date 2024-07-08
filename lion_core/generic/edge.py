"""Hypergraph components for the Lion framework.

This module defines the core classes for representing hypergraphs and edges
in the Lion framework. It provides a flexible and extensible foundation for
graph-based data structures and algorithms.

Classes:
    HyperEdge: Represents a hyperedge connecting multiple nodes in a hypergraph.
    Edge: Represents a directed or undirected edge between two nodes.
"""

from typing import Any, Set
from pydantic import Field, field_validator, BaseModel, ConfigDict
from .component import Component
from lion_core.abc.event import Condition
from ..util.sys_util import SysUtil
from .base_hyper_edge import DirectedMixin
from .hyper_edge import HyperEdge


class Edge(HyperEdge):
    """Represents a directed or undirected edge between two nodes in a graph.

    This class extends the HyperEdge class to represent edges in a graph,
    providing methods for validation and basic operations. Edge properties
    can be stored and retrieved using the metadata field inherited from the
    Component class.

    Attributes:
        head (str): The identifier of the head node of the edge.
        tail (str): The identifier of the tail node of the edge.
    """

    # need correcting
    # # head: str = Field(..., description="The identifier of the head node of the edge.")
    # # tail: str = Field(..., description="The identifier of the tail node of the edge.")

    # def __init__(self, head: Any, tail: Any, **data: Any):
    #     """Initialize an Edge instance.

    #     Args:
    #         head (Any): The head node of the edge.
    #         tail (Any): The tail node of the edge.
    #         **data: Additional keyword arguments for other attributes.
    #     """
    #     super().__init__([head, tail], **data)
    #     self.head = SysUtil.get_lion_id(head)
    #     self.tail = SysUtil.get_lion_id(tail)

    @field_validator("head", "tail", mode="before")
    @classmethod
    def validate_node_id(cls, value: Any) -> str:
        """Validate and convert node identifiers.

        Args:
            value (Any): The value to be validated and converted.

        Returns:
            str: The validated and converted node identifier.
        """
        return SysUtil.get_lion_id(value)

    def __contains__(self, item: Any) -> bool:
        """Check if the given item is the head or tail of the edge.

        Args:
            item (Any): The item to check.

        Returns:
            bool: True if the item is the head or tail of the edge,
                  False otherwise.
        """
        return SysUtil.get_lion_id(item) in (self.head, self.tail)

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
            f"weight={self.meta_get('weight', 1.0):.2f}, directed={self.directed})"
        )

    def __repr__(self) -> str:
        """Return a detailed string representation of the Edge.

        Returns:
            str: A detailed string representation of the Edge.
        """
        return (
            f"Edge(ln_id={self.ln_id}, head={self.head}, tail={self.tail}, "
            f"weight={self.meta_get('weight', 1.0)}, directed={self.directed}, "
            f"label={self.label!r}, condition={self.condition!r}, "
            f"metadata={self.metadata}, content={self.content!r})"
        )
