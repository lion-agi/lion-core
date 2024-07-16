"""HyperEdge module for the Lion framework.

This module defines a flexible HyperEdge class that can be instantiated
with different properties based on user needs.

Classes:
    HyperEdge: Flexible hyperedge that can be directed and/or weighted.
"""

from typing import Any, List

from .base_hyper_edge import BaseHyperEdge, DirectedMixin, WeightedMixin
from ..util.sys_util import SysUtil


class HyperEdge(BaseHyperEdge):
    """Flexible hyperedge that can be directed and/or weighted.

    This class extends BaseHyperEdge and can incorporate DirectedMixin
    and WeightedMixin based on initialization parameters.

    Attributes:
        Inherits all attributes from BaseHyperEdge.
        May include additional attributes from DirectedMixin and WeightedMixin.
    """

    def __init__(
        self,
        nodes: List[Any],
        directed: bool = False,
        weighted: bool = False,
        **data: Any,
    ):
        """Initialize a HyperEdge instance.

        Args:
            nodes: List of nodes to be connected by this hyperedge.
            directed: Whether the hyperedge is directed. Default is False.
            weighted: Whether the hyperedge is weighted. Default is False.
            **data: Additional keyword arguments for other attributes.
        """
        # Dynamically create a new class with the requested mixins
        class_bases = [BaseHyperEdge]
        if directed:
            class_bases.append(DirectedMixin)
        if weighted:
            class_bases.append(WeightedMixin)

        DynamicHyperEdge = type("DynamicHyperEdge", tuple(class_bases), {})

        # Initialize with the dynamic class
        super().__init__(**data)
        DynamicHyperEdge.__init__(self, nodes=nodes, **data)

        if directed:
            self.nodes = {
                "head": set(),
                "tail": set(SysUtil.get_lion_id(node) for node in nodes),
            }
        else:
            self.nodes = {"nodes": set(SysUtil.get_lion_id(node) for node in nodes)}

    def add_node(self, node: Any, as_head: bool = False) -> None:
        """Add a node to the hyperedge.

        Args:
            node: The node to be added.
            as_head: Whether to add the node to the head (for directed hyperedges).
                     Ignored for undirected hyperedges.
        """
        if hasattr(self, "is_directed") and self.is_directed:
            super().add_node(node, as_head)
        else:
            node_id = SysUtil.get_lion_id(node)
            self.nodes["nodes"].add(node_id)

    def remove_node(self, node: Any) -> None:
        """Remove a node from the hyperedge.

        Args:
            node: The node to be removed.

        Raises:
            ValueError: If the node is not in the hyperedge.
        """
        if hasattr(self, "is_directed") and self.is_directed:
            super().remove_node(node)
        else:
            node_id = SysUtil.get_lion_id(node)
            if node_id in self.nodes["nodes"]:
                self.nodes["nodes"].remove(node_id)
            else:
                raise ValueError(f"Node {node_id} not found in the hyperedge.")

    def __str__(self) -> str:
        """Return a concise string representation of the HyperEdge.

        Returns:
            A string representation of the HyperEdge.
        """
        directed_str = "directed" if hasattr(self, "is_directed") else "undirected"
        weighted_str = "weighted" if hasattr(self, "weights") else "unweighted"
        return f"HyperEdge(nodes={len(self)}, {directed_str}, {weighted_str})"

    def __repr__(self) -> str:
        """Return a detailed string representation of the HyperEdge.

        Returns:
            A detailed string representation of the HyperEdge.
        """
        return (
            f"HyperEdge(ln_id={self.ln_id}, nodes={self.nodes}, "
            f"directed={hasattr(self, 'is_directed')}, "
            f"weighted={hasattr(self, 'weights')}, "
            f"labels={self.labels}, condition={self.condition!r}, "
            f"metadata={self.metadata}, content={self.content!r})"
        )


# File: lion_core/generic/hyper_edge.py
