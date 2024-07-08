"""Base HyperEdge and mixins for the Lion framework.

This module defines the base HyperEdge class and mixins for directed and
weighted hyperedges.

Classes:
    BaseHyperEdge: Represents a basic hyperedge in a hypergraph.
    DirectedMixin: Mixin for directed hyperedges.
    WeightedMixin: Mixin for weighted hyperedges.
"""

from typing import Any, Dict, List, Set
from pydantic import Field, field_validator

from .component import Component
from .edge_condition import EdgeCondition
from ..util.sys_util import SysUtil


class BaseHyperEdge(Component):
    """Represents a basic hyperedge connecting multiple nodes in a hypergraph.

    This class extends the Component class to represent basic hyperedges,
    providing essential attributes and methods for node management.

    Attributes:
        nodes (Dict[str, Set[str]]): Dictionary of node identifiers.
        condition (EdgeCondition | None): Optional condition for the hyperedge.
        labels (List[str]): List of labels for the hyperedge.
    """

    nodes: Dict[str, Set[str]] = Field(
        default_factory=lambda: {"nodes": set()},
        description="Dictionary of node identifiers.",
    )
    condition: EdgeCondition | None = Field(
        default=None, description="Optional condition for the hyperedge."
    )
    labels: List[str] = Field(
        default_factory=list,
        description="List of labels for the hyperedge.",
    )

    @field_validator("nodes", mode="before")
    @classmethod
    def validate_nodes(cls, v: Any) -> Dict[str, Set[str]]:
        """Validate and convert the nodes dictionary.

        Args:
            v: The value to be validated and converted.

        Returns:
            The validated and converted dictionary of node identifiers.

        Raises:
            ValueError: If the input is not a dictionary, list, or set.
        """
        if isinstance(v, dict):
            return {
                k: {SysUtil.get_lion_id(node) for node in nodes}
                for k, nodes in v.items()
            }
        if isinstance(v, (list, set)):
            return {"nodes": {SysUtil.get_lion_id(node) for node in v}}
        raise ValueError("Nodes must be a dictionary, list, or set.")

    async def apply_condition(self, *args: Any, **kwargs: Any) -> bool:
        """Apply the hyperedge condition.

        This method evaluates the hyperedge's condition. If no condition is set,
        it always returns True.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            True if the condition is met or if there's no condition,
            False otherwise.
        """
        if not self.condition:
            return True
        return await self.condition.apply(*args, **kwargs)

    def __contains__(self, item: Any) -> bool:
        """Check if the given item is part of the hyperedge.

        Args:
            item: The item to check for membership in the hyperedge.

        Returns:
            True if the item is in the hyperedge, False otherwise.
        """
        item_id = SysUtil.get_lion_id(item)
        return any(item_id in node_set for node_set in self.nodes.values())

    def __len__(self) -> int:
        """Return the total number of nodes in the hyperedge.

        Returns:
            The total number of nodes in the hyperedge.
        """
        return sum(len(node_set) for node_set in self.nodes.values())


# ponder on it
class DirectedMixin:
    """Mixin for directed hyperedges.

    This mixin adds directional properties to a hyperedge.
    """

    @property
    def is_directed(self) -> bool:
        """Indicate that this is a directed hyperedge."""
        return True

    def add_node(self, node: Any, as_head: bool = False) -> None:
        """Add a node to the directed hyperedge.

        Args:
            node: The node to be added.
            as_head: If True, add the node to the head set. Otherwise, add to the tail set.
        """
        node_id = SysUtil.get_lion_id(node)
        key = "head" if as_head else "tail"
        self.nodes[key].add(node_id)

    def remove_node(self, node: Any) -> None:
        """Remove a node from the directed hyperedge.

        Args:
            node: The node to be removed.

        Raises:
            ValueError: If the node is not in the hyperedge.
        """
        node_id = SysUtil.get_lion_id(node)
        for node_set in self.nodes.values():
            if node_id in node_set:
                node_set.remove(node_id)
                return
        raise ValueError(f"Node {node_id} not found in the hyperedge.")


# class WeightedMixin:
#     """Mixin for weighted hyperedges.

#     This mixin adds weight-related methods to a hyperedge.
#     """

#     weights: Dict[str, float] = Field(
#         default_factory=dict,
#         description="Dictionary of node weights.",
#     )

#     def set_weight(self, node: Any, weight: float) -> None:
#         """Set the weight for a node in the hyperedge.

#         Args:
#             node: The node to set the weight for.
#             weight: The weight to set.
#         """
#         node_id = SysUtil.get_lion_id(node)
#         self.weights[node_id] = weight

#     def get_weight(self, node: Any) -> float:
#         """Get the weight of a node in the hyperedge.

#         Args:
#             node: The node to get the weight for.

#         Returns:
#             The weight of the node, or 1.0 if not set.
#         """
#         node_id = SysUtil.get_lion_id(node)
#         return self.weights.get(node_id, 1.0)


# File: lion_core/generic/base_hyper_edge.py
