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
from ..primitive.util import get_lion_id


class EdgeCondition(AbstractCondition, BaseModel):
    """Represents a condition associated with an edge in the Lion framework.

    This class combines AbstractCondition characteristics with Pydantic's
    BaseModel for robust data validation and serialization.

    Attributes:
        source (Any): The source for condition check.
    """

    source: Any = Field(
        default=None,
        title="Source",
        description="The source for condition check",
    )

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
    )

    async def applies(self, *args: Any, **kwargs: Any) -> bool:
        """Check if the condition applies.

        This method should be implemented by subclasses to define
        the specific condition logic.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            bool: True if the condition applies, False otherwise.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError("Subclasses must implement applies method.")


class HyperEdge(Component):
    """Represents a hyperedge connecting multiple nodes in a hypergraph.

    This class extends the Component class to represent hyperedges,
    providing methods for node management and hypergraph-specific operations.

    Attributes:
        nodes (Set[str]): Set of node identifiers connected by this hyperedge.
        condition (EdgeCondition | None): Optional condition for the hyperedge.
        label (str | None): Optional label for the hyperedge.
        directed (bool): Indicates if the hyperedge is directed.
    """

    nodes: Set[str] = Field(
        default_factory=set,
        description="Set of node identifiers connected by this hyperedge.",
    )
    condition: EdgeCondition | None = Field(
        default=None, description="Optional condition for the hyperedge."
    )
    label: str | None = Field(
        default=None, description="Optional label for the hyperedge."
    )
    directed: bool = Field(
        default=False, description="Indicates if the hyperedge is directed."
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

    async def check_condition(self, obj: Any) -> bool:
        """Check if the hyperedge condition is met for the given object.

        This method evaluates the hyperedge's condition against the provided
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
        return f"HyperEdge(nodes={len(self.nodes)}, directed={self.directed})"

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

    head: str = Field(..., description="The identifier of the head node of the edge.")
    tail: str = Field(..., description="The identifier of the tail node of the edge.")

    def __init__(self, head: Any, tail: Any, **data: Any):
        """Initialize an Edge instance.

        Args:
            head (Any): The head node of the edge.
            tail (Any): The tail node of the edge.
            **data: Additional keyword arguments for other attributes.
        """
        super().__init__([head, tail], **data)
        self.head = get_lion_id(head)
        self.tail = get_lion_id(tail)

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
