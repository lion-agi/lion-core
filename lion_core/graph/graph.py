from typing import Any
from collections import deque

from pydantic import Field

from lion_core.abc import Event
from lion_core.sys_utils import SysUtil
from lion_core.generic.pile import Pile, pile
from lion_core.exceptions import LionRelationError
from lion_core.graph.node import Node
from lion_core.graph.edge import Edge


class Graph(Node):
    """
    Represents a graph structure containing nodes and edges.

    This class models a graph with internal nodes and edges, providing
    methods for graph manipulation and analysis.

    Attributes:
        internal_nodes (Pile): The internal nodes of the graph.
        internal_edges (Pile): The internal edges of the graph.
    """

    internal_nodes: Pile = Field(
        default_factory=lambda: pile({}, {Node}),
        description="The internal nodes of the graph.",
    )
    internal_edges: Pile = Field(
        default_factory=pile,
        description="The internal edges of the graph.",
    )

    def __contains__(self, other: Any) -> bool:
        """Check if a node or edge is in the graph."""
        return other in self.internal_nodes or other in self.internal_edges

    def has_dangling_edges(self) -> bool:
        """Check if the graph has any dangling edges."""
        return any(edge.is_dangling(self) for edge in self.internal_edges)

    def add_node(self, node: Node) -> None:
        """
        Add a node to the graph.

        Args:
            node: The node to add.

        Raises:
            LionRelationError: If the node already exists in the graph.
        """
        if node not in self.internal_nodes:
            self.internal_nodes.include(node)
            return
        raise LionRelationError(f"Node {node} already exists in the graph.")

    def remove_node(self, node: Node) -> None:
        """
        Remove a node from the graph and update related edges.

        Args:
            node: The node to remove.

        Raises:
            LionRelationError: If the node is not found or its removal
                               would cause dangling edges.
        """
        if node not in self.internal_nodes:
            raise LionRelationError(f"Node {node} not found in the graph.")

        related = []
        to_remove = []

        for edge in self.internal_edges:
            if node in edge:
                related.append(edge)
                edge_copy = SysUtil.copy(edge)
                edge_copy.remove_node(node)
                if edge_copy.is_dangling(self):
                    to_remove.append(edge)

        if to_remove:
            self.internal_edges.exclude(to_remove)

            if self.has_dangling_edges():
                self.internal_edges.include(to_remove)
                raise LionRelationError("Removing this node will cause dangling edges.")

        self.internal_nodes.exclude(node)

    def add_edge(self, node1: Node | Any, node2: Any, edge: Edge | None = None) -> None:
        """
        Add an edge between nodes in the graph.

        Args:
            node1: The source node(s) for the edge.
            node2: The target node(s) for the edge.
            edge: An optional Edge object to use. If None, a new Edge is created.
        """
        if edge is None:
            edge = Edge()

        node1 = [node1] if not isinstance(node1, list) else node1
        node2 = [node2] if not isinstance(node2, list) else node2

        for node in node1:
            edge.add_node(node, direction="head")

        for node in node2:
            edge.add_node(node, direction="tail")

        self.internal_nodes.include(node1 + node2)
        self.internal_edges.include(edge)

    def remove_edge(self, edge: Edge | str) -> None:
        """Remove an edge from the graph."""
        self.internal_edges.exclude(edge)

    def find_node_edge(self, node: Any, direction: str = "head") -> Pile[Edge]:
        """
        Find edges connected to a node in a specific direction.

        Args:
            node: The node to find edges for.
            direction: The direction to search ("head" or "tail").

        Returns:
            A Pile of Edges connected to the node in the specified direction.
        """
        return pile(
            [
                edge
                for edge in self.internal_edges
                if node in edge.edge_info.get([direction, "nodes"], [])
            ]
        )

    def is_acyclic(self) -> bool:
        """
        Check if the graph is acyclic (contains no cycles).

        Returns:
            bool: True if the graph is acyclic, False otherwise.
        """
        node_ids = list(self.internal_nodes.keys())
        check_deque = deque(node_ids)
        check_dict: dict[str, int] = {
            key: 0 for key in node_ids
        }  # 0: not visited, 1: temp, 2: perm

        def visit(node_id: str) -> bool:
            if check_dict[node_id] == 2:
                return True
            if check_dict[node_id] == 1:
                return False

            check_dict[node_id] = 1

            # Check all outgoing edges
            for edge in self.find_node_edge(node_id, "head"):
                # For each head of the edge, continue the traversal
                for head in edge.edge_info.get(["head", "nodes"], []):
                    if not visit(head):
                        return False

            check_dict[node_id] = 2
            return True

        while check_deque:
            node_id = check_deque.pop()
            if check_dict[node_id] == 0:  # Only visit unvisited nodes
                if not visit(node_id):
                    return False

        return True

    def get_heads(self) -> Pile:
        """
        Get all head nodes in the graph.

        Returns:
            Pile: A Pile containing all head nodes.
        """

        def is_head(node: Node) -> bool:
            return all(
                [
                    not self.find_node_edge(node, "head"),
                    self.find_node_edge(node, "tail"),
                    not isinstance(node, Event),
                ]
            )

        return pile([node for node in self.internal_nodes if is_head(node)])


# File: lion_core/graph/graph.py
