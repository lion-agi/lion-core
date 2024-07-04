"""Node module for the Lion framework.

This module defines the Node class, representing nodes in graph-like
structures. It enables the construction and manipulation of complex
relational networks within the Lion framework.

Classes:
    Node: Represents a node in a graph structure with relational capabilities.
"""

from __future__ import annotations
from typing import Any, List, Dict, Optional, Union, Generic, TypeVar

from pydantic import Field

from lion_core.abc import AbstractCondition, Relatable, LionRelationError
from lion_core.primitive import Pile, pile, get_lion_id
from .component import Component
from .edge import Edge
from .hyperedge import HyperEdge

T = TypeVar("T")


class Node(Component, Relatable, Generic[T]):
    """Node in a graph structure, can connect to other nodes via edges.

    Extends `Component` by incorporating relational capabilities, allowing
    nodes to connect through 'in' and 'out' directed edges, representing
    incoming and outgoing relationships.

    Attributes:
        relations (Dict[str, Pile]): Dictionary holding 'Pile' instances
            for incoming ('in') and outgoing ('out') edges.
        value (T): The value stored in the node.
    """

    relations: Dict[str, Pile] = Field(
        default_factory=lambda: {"in": pile(), "out": pile()},
        description="The relations of the node.",
    )
    value: T = Field(description="The value stored in the node.")

    def __init__(self, value: T, **data: Any):
        """Initialize a Node instance.

        Args:
            value (T): The value to be stored in the node.
            **data: Additional keyword arguments for other attributes.
        """
        super().__init__(**data)
        self.value = value

    @property
    def edges(self) -> Pile[Union[Edge, HyperEdge]]:
        """Get unified view of all incoming and outgoing edges."""
        return self.relations["in"] + self.relations["out"]

    @property
    def related_nodes(self) -> List[str]:
        """Get list of all unique node IDs directly related to this node."""
        related = set()
        for edge in self.edges:
            if isinstance(edge, Edge):
                related.add(edge.head if edge.tail == self.ln_id else edge.tail)
            elif isinstance(edge, HyperEdge):
                related.update(edge.nodes - {self.ln_id})
        return list(related)

    @property
    def node_relations(self) -> Dict[str, Dict[str, List[Union[Edge, HyperEdge]]]]:
        """Get categorized view of direct relationships into groups."""
        relations = {"out": {}, "in": {}}
        for direction in ["out", "in"]:
            for edge in self.relations[direction]:
                if isinstance(edge, Edge):
                    node_id = edge.tail if direction == "out" else edge.head
                    relations[direction].setdefault(node_id, []).append(edge)
                elif isinstance(edge, HyperEdge):
                    for node_id in edge.nodes - {self.ln_id}:
                        relations[direction].setdefault(node_id, []).append(edge)
        return relations

    @property
    def predecessors(self) -> List[str]:
        """Get list of IDs of nodes with direct incoming relation to this."""
        return list(self.node_relations["in"].keys())

    @property
    def successors(self) -> List[str]:
        """Get list of IDs of nodes with direct outgoing relation from this."""
        return list(self.node_relations["out"].keys())

    def relate(
        self,
        node: Node,
        direction: str = "out",
        condition: Optional[AbstractCondition] = None,
        label: Optional[str] = None,
        bundle: bool = False,
    ) -> None:
        """Establish directed relationship from this node to another.

        Args:
            node (Node): Target node to relate to.
            direction (str): Direction of edge ('in' or 'out'). Default 'out'.
            condition (Optional[AbstractCondition]): Optional condition for the edge.
            label (Optional[str]): Optional label for the edge.
            bundle (bool): Whether to bundle edge with others. Default False.

        Raises:
            ValueError: If direction is neither 'in' nor 'out'.
        """
        if direction not in ["in", "out"]:
            raise ValueError(
                f"Invalid value for direction: {direction}, must be 'in' or 'out'"
            )

        edge = Edge(
            head=self if direction == "out" else node,
            tail=node if direction == "out" else self,
            condition=condition,
            bundle=bundle,
            label=label,
        )

        self.relations[direction].include(edge)
        node.relations["in" if direction == "out" else "out"].include(edge)

    def remove_edge(self, node: Node, edge: Union[Edge, HyperEdge, str]) -> bool:
        """Remove specified edge or all edges between this and another node.

        Args:
            node (Node): Other node involved in edge.
            edge (Union[Edge, HyperEdge, str]): Specific edge to remove or 'all'.

        Returns:
            bool: True if edge(s) successfully removed, False otherwise.

        Raises:
            LionRelationError: If removal fails or edge does not exist.
        """
        edge_piles = [
            self.relations["in"],
            self.relations["out"],
            node.relations["in"],
            node.relations["out"],
        ]

        if not all(pile.exclude(edge) for pile in edge_piles):
            raise LionRelationError("Failed to remove edge between nodes.")
        return True

    def unrelate(self, node: Node, edge: Union[Edge, HyperEdge, str] = "all") -> bool:
        """Remove all or specific relationships between this and another node.

        Args:
            node (Node): Other node to unrelate from.
            edge (Union[Edge, HyperEdge, str]): Specific edge to remove or 'all'.

        Returns:
            bool: True if relationships successfully removed, False otherwise.

        Raises:
            LionRelationError: If operation fails to unrelate nodes.
        """
        if edge == "all":
            edges = self.node_relations["out"].get(
                node.ln_id, []
            ) + self.node_relations["in"].get(node.ln_id, [])
        else:
            edges = [get_lion_id(edge)]

        if not edges:
            raise LionRelationError(f"Node is not related to {node.ln_id}.")

        try:
            for edge_id in edges:
                self.remove_edge(node, edge_id)
            return True
        except LionRelationError as e:
            raise e

    def __str__(self) -> str:
        """Return a string representation of the node."""
        return (
            f"{self.__class__.__name__}("
            f"ln_id={self.ln_id[:8]}..., "
            f"value={self.value}, "
            f"in_relations={len(self.relations['in'])}, "
            f"out_relations={len(self.relations['out'])})"
        )

    def __repr__(self) -> str:
        """Return a detailed string representation of the node."""
        return (
            f"{self.__class__.__name__}("
            f"ln_id={self.ln_id}, "
            f"value={self.value!r}, "
            f"in_relations={len(self.relations['in'])}, "
            f"out_relations={len(self.relations['out'])}, "
            f"metadata={self.metadata})"
        )


# Path: lion_core/generic/node.py
