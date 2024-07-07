"""Relation module for the Lion framework.

This module defines the base Relation class for representing relations
in graph structures within the Lion framework. It combines Relatable and
Component characteristics to provide a robust foundation for graph-based
relationships.

Classes:
    Relation: Base class for representing relations in graphs.
"""

from typing import Any

from pydantic import Field

from lion_core.abc.concept import Relatable
from ..element.component import Component
from .edge_condition import EdgeCondition


class Relation(Relatable, Component):
    """Base class for representing relations in a graph.

    This class combines Relatable and Component characteristics to provide
    a flexible and extensible representation of relations in graph structures.

    Attributes:
        condition (EdgeCondition | None): Optional condition for the relation.
        label (str | None): Optional label for the relation.
        directed (bool): Indicates if the relation is directed.
    """

    condition: EdgeCondition | None = Field(
        default=None, description="Optional condition for the relation."
    )
    label: str | None = Field(
        default=None, description="Optional label for the relation."
    )
    directed: bool = Field(
        default=False, description="Indicates if the relation is directed."
    )

    async def check_condition(self, obj: Any) -> bool:
        """Check if the relation condition is met for the given object.

        This method evaluates the relation's condition against the provided
        object. If no condition is set, it always returns True.

        Args:
            obj (Any): The object to check the condition against.

        Returns:
            bool: True if the condition is met or if there's no condition,
                  False otherwise.
        """
        if not self.condition:
            return True
        return await self.condition.applies(obj)

    def __str__(self) -> str:
        """Return a string representation of the Relation."""
        return (
            f"{self.__class__.__name__}("
            f"label={self.label}, "
            f"directed={self.directed}, "
            f"condition={'set' if self.condition else 'not set'})"
        )

    def __repr__(self) -> str:
        """Return a detailed string representation of the Relation."""
        return (
            f"{self.__class__.__name__}("
            f"ln_id={repr(self.ln_id)}, "
            f"label={repr(self.label)}, "
            f"directed={self.directed}, "
            f"condition={repr(self.condition)})"
        )


# Path: lion_core/generic/relation.py


"""HyperEdge module for the Lion framework.

This module defines the HyperEdge class for representing hyperedges in
hypergraph structures within the Lion framework. It extends the Relation
class to provide specific functionality for hyperedge representation and
manipulation.

Classes:
    HyperEdge: Represents a hyperedge connecting multiple nodes in a hypergraph.
"""

from typing import Any, Set

from pydantic import Field, field_validator

from lion_core.primitive.util import get_lion_id
from ..generic.relation import Relation


class HyperEdge(Relation):
    """Represents a hyperedge connecting multiple nodes in a hypergraph.

    This class extends the Relation class to represent hyperedges,
    providing methods for node management and hypergraph-specific operations.
    Node weights and other properties are stored in the metadata field
    inherited from the Component class.

    Attributes:
        nodes (Set[str]): Set of node identifiers connected by this hyperedge.
    """

    nodes: Set[str] = Field(
        default_factory=set,
        description="Set of node identifiers connected by this hyperedge.",
    )

    def __init__(self, nodes: list[Any], **data: Any):
        """Initialize a HyperEdge instance.

        Args:
            nodes (list[Any]): List of nodes to be connected by this hyperedge.
            **data: Additional keyword arguments for other attributes.
        """
        super().__init__(**data)
        self.nodes = {get_lion_id(node) for node in nodes}
        if self.directed:
            self._meta_set("source_nodes", set())
            self._meta_set("target_nodes", set())

    @field_validator("nodes", mode="before")
    @classmethod
    def validate_node_id(cls, v: Any) -> Set[str]:
        """Validate and convert the node set.

        Args:
            v (Any): The value to be validated and converted.

        Returns:
            Set[str]: The validated and converted set of node identifiers.
        """
        return {get_lion_id(node) for node in v}

    def add_node(self, node: Any, weight: float = 1.0) -> None:
        """Add a node to the hyperedge with an optional weight.

        Args:
            node (Any): The node to be added to the hyperedge.
            weight (float, optional): The weight of the node in the hyperedge.
                Defaults to 1.0.
        """
        node_id = get_lion_id(node)
        self.nodes.add(node_id)
        self._meta_set(f"node_weights.{node_id}", weight)

    def remove_node(self, node: Any) -> None:
        """Remove a node from the hyperedge.

        Args:
            node (Any): The node to be removed from the hyperedge.

        Raises:
            KeyError: If the node is not in the hyperedge.
        """
        node_id = get_lion_id(node)
        self.nodes.remove(node_id)
        self._meta_pop(f"node_weights.{node_id}", None)
        if self.directed:
            self._meta_get("source_nodes", set()).discard(node_id)
            self._meta_get("target_nodes", set()).discard(node_id)

    def set_direction(self, sources: list[Any], targets: list[Any]) -> None:
        """Set the direction of the hyperedge.

        Args:
            sources (list[Any]): List of source nodes.
            targets (list[Any]): List of target nodes.

        Raises:
            ValueError: If the hyperedge is not directed.
        """
        if not self.directed:
            raise ValueError("This hyperedge is not directed")
        self._meta_set("source_nodes", {get_lion_id(node) for node in sources})
        self._meta_set("target_nodes", {get_lion_id(node) for node in targets})

    def get_node_weight(self, node: Any) -> float:
        """Get the weight of a node in the hyperedge.

        Args:
            node (Any): The node to get the weight for.

        Returns:
            float: The weight of the node in the hyperedge.

        Raises:
            KeyError: If the node is not in the hyperedge.
        """
        node_id = get_lion_id(node)
        if node_id not in self.nodes:
            raise KeyError(f"Node {node_id} is not in the hyperedge")
        return self._meta_get(f"node_weights.{node_id}", 1.0)

    def set_node_weight(self, node: Any, weight: float) -> None:
        """Set the weight of a node in the hyperedge.

        Args:
            node (Any): The node to set the weight for.
            weight (float): The weight to set for the node.

        Raises:
            KeyError: If the node is not in the hyperedge.
        """
        node_id = get_lion_id(node)
        if node_id not in self.nodes:
            raise KeyError(f"Node {node_id} is not in the hyperedge")
        self._meta_set(f"node_weights.{node_id}", weight)

    def __contains__(self, item: Any) -> bool:
        """Check if the given item is part of the hyperedge.

        Args:
            item (Any): The item to check for membership in the hyperedge.

        Returns:
            bool: True if the item is in the hyperedge, False otherwise.
        """
        return get_lion_id(item) in self.nodes

    def __len__(self) -> int:
        """Return the number of nodes in the hyperedge.

        Returns:
            int: The number of nodes in the hyperedge.
        """
        return len(self.nodes)

    def __str__(self) -> str:
        """Return a concise string representation of the HyperEdge.

        Returns:
            str: A string representation of the HyperEdge.
        """
        return f"HyperEdge(nodes={len(self.nodes)}, " f"directed={self.directed})"

    def __repr__(self) -> str:
        """Return a detailed string representation of the HyperEdge.

        Returns:
            str: A detailed string representation of the HyperEdge.
        """
        return (
            f"HyperEdge(ln_id={self.ln_id}, nodes={self.nodes}, "
            f"directed={self.directed}, "
            f"label={self.label!r}, condition={self.condition!r}, "
            f"metadata={self.metadata}, content={self.content!r})"
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the hyperedge to a dictionary representation.

        Returns:
            dict[str, Any]: A dictionary representation of the hyperedge.
        """
        data = super().to_dict()
        data.update(
            {
                "nodes": list(self.nodes),
                "node_weights": self._meta_get("node_weights", {}),
                "source_nodes": list(self._meta_get("source_nodes", set())),
                "target_nodes": list(self._meta_get("target_nodes", set())),
            }
        )
        return data


# Path: lion_core/generic/hypergraph.py
