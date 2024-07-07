"""Graph and Tree module for the Lion framework.

This module defines the Graph and Tree classes, representing graph and tree
structures within the Lion framework. It provides methods for managing nodes
and edges, as well as tree-specific operations.

Classes:
    Graph: Represents a graph structure with nodes and edges.
    Tree: Represents a tree structure, extending the graph with tree-specific functionalities.
"""

import contextlib
from collections import deque
from typing import Any, Optional, List

from pydantic import Field

from lion_core.libs import to_list, SysUtil
from lion_core.abc import (
    AbstractCondition,
    LionTypeError,
    ItemNotFoundError,
    Actionable,
)
from lion_core.primitive import pile, Pile
from ..component.edge import Edge
from ..component.node import Node


class Graph(Node):
    """Represents a graph structure with nodes and edges."""

    internal_nodes: Pile = pile()

    @property
    def internal_edges(self) -> Pile[Edge]:
        """Return a pile of all edges in the graph."""
        return pile(
            {edge.ln_id: edge for node in self.internal_nodes for edge in node.edges},
            Edge,
        )

    def is_empty(self) -> bool:
        """Check if the graph is empty (has no nodes)."""
        return self.internal_nodes.is_empty()

    def clear(self):
        """Clear all nodes and edges from the graph."""
        self.internal_nodes.clear()

    def add_edge(
        self,
        head: Node,
        tail: Node,
        condition: Optional[AbstractCondition] = None,
        bundle: bool = False,
        label: Optional[str] = None,
        **kwargs,
    ):
        """Add an edge between two nodes in the graph."""
        if isinstance(head, Actionable):
            raise LionTypeError("Actionable nodes cannot be related as head.")
        if isinstance(tail, Actionable):
            bundle = True

        self.internal_nodes.include(head)
        self.internal_nodes.include(tail)

        head.relate(
            tail,
            direction="out",
            condition=condition,
            label=label,
            bundle=bundle,
            **kwargs,
        )

    def remove_edge(self, edge: Any) -> bool:
        """Remove an edge from the graph."""
        edge = edge if isinstance(edge, list) else [edge]
        for i in edge:
            if i not in self.internal_edges:
                raise ItemNotFoundError(f"Edge {i} does not exist in structure.")
            with contextlib.suppress(ItemNotFoundError):
                self._remove_edge(i)

    def add_node(self, node: Any) -> None:
        """Add a node to the graph."""
        self.internal_nodes.update(node)

    def get_node(self, item, default=...):
        """Get a node from the graph by its identifier."""
        return self.internal_nodes.get(item, default)

    def get_node_edges(
        self,
        node: Node | str,
        direction: str = "both",
        label: Optional[List[str] | str] = None,
    ) -> Optional[Pile[Edge]]:
        """Get the edges of a node in the specified direction and with the given label."""
        node = self.internal_nodes[node]
        edges = None
        match direction:
            case "both":
                edges = node.edges
            case "head" | "predecessor" | "outgoing" | "out" | "predecessors":
                edges = node.relations["out"]
            case "tail" | "successor" | "incoming" | "in" | "successors":
                edges = node.relations["in"]

        if label:
            return (
                pile(
                    [
                        edge
                        for edge in edges
                        if edge.label in to_list(label, dropna=True, flatten=True)
                    ]
                )
                if edges
                else None
            )
        return pile(edges) if edges else None

    def pop_node(self, item, default=...):
        """Remove and return a node from the graph by its identifier."""
        return self.internal_nodes.pop(item, default)

    def remove_node(self, item):
        """Remove a node from the graph by its identifier."""
        return self.internal_nodes.remove(item)

    def _remove_edge(self, edge: Edge | str) -> bool:
        """Remove a specific edge from the graph."""
        if edge not in self.internal_edges:
            raise ItemNotFoundError(f"Edge {edge} does not exist in structure.")

        edge = self.internal_edges[edge]
        head: Node = self.internal_nodes[edge.head]
        tail: Node = self.internal_nodes[edge.tail]

        head.unrelate(tail, edge=edge)
        return True

    def get_heads(self) -> Pile:
        """Get all head nodes in the graph."""
        return pile(
            [
                node
                for node in self.internal_nodes
                if node.relations["in"].is_empty() and not isinstance(node, Actionable)
            ]
        )

    def is_acyclic(self) -> bool:
        """Check if the graph is acyclic (contains no cycles)."""
        node_ids = list(self.internal_nodes.keys())
        check_deque = deque(node_ids)
        check_dict = {key: 0 for key in node_ids}  # 0: not visited, 1: temp, 2: perm

        def visit(key):
            if check_dict[key] == 2:
                return True
            elif check_dict[key] == 1:
                return False

            check_dict[key] = 1

            for edge in self.internal_nodes[key].relations["out"]:
                check = visit(edge.tail)
                if not check:
                    return False

            check_dict[key] = 2
            return True

        while check_deque:
            key = check_deque.pop()
            check = visit(key)
            if not check:
                return False
        return True

    def to_networkx(self, **kwargs) -> Any:
        """Convert the graph to a NetworkX graph object."""
        SysUtil.check_import("networkx")
        from networkx import DiGraph  # type: ignore

        g = DiGraph(**kwargs)
        for node in self.internal_nodes:
            node_info = node.to_dict()
            node_info.pop("ln_id")
            node_info.update({"class_name": node.class_name})
            g.add_node(node.ln_id, **node_info)

        for _edge in self.internal_edges:
            edge_info = _edge.to_dict()
            edge_info.pop("ln_id")
            edge_info.update({"class_name": _edge.class_name})
            source_node_id = edge_info.pop("head")
            target_node_id = edge_info.pop("tail")
            g.add_edge(source_node_id, target_node_id, **edge_info)

        return g

    def display(self, **kwargs):
        """Display the graph using NetworkX and Matplotlib."""
        SysUtil.check_import("networkx")
        SysUtil.check_import("matplotlib", "pyplot")

        import networkx as nx  # type: ignore
        import matplotlib.pyplot as plt  # type: ignore

        g = self.to_networkx(**kwargs)
        pos = nx.spring_layout(g)
        nx.draw(
            g,
            pos,
            edge_color="black",
            width=1,
            linewidths=1,
            node_size=500,
            node_color="orange",
            alpha=0.9,
            labels=nx.get_node_attributes(g, "class_name"),
        )

        labels = nx.get_edge_attributes(g, "label")
        labels = {k: v for k, v in labels.items() if v}

        if labels:
            nx.draw_networkx_edge_labels(
                g, pos, edge_labels=labels, font_color="purple"
            )

        plt.axis("off")
        plt.show()

    def size(self) -> int:
        """Return the number of nodes in the graph."""
        return len(self.internal_nodes)


class Tree(Graph):
    """Represents a tree structure, extending the graph with tree-specific functionalities.

    Manages parent-child relationships within the tree.

    Attributes:
        root (Node | None): The root node of the tree. Defaults to None.
    """

    root: Optional[Node] = Field(
        default=None, description="The root node of the tree graph."
    )

    def add_child(self, parent: Node, child: Node) -> None:
        """Add a child node to a parent node in the tree.

        Args:
            parent (Node): The parent node.
            child (Node): The child node to be added.
        """
        self.add_edge(parent, child, label="parent-child")
        if self.root is None:
            self.root = parent

    def get_children(self, node: Node) -> List[Node]:
        """Get the children of a given node in the tree.

        Args:
            node (Node): The node to get children for.

        Returns:
            List[Node]: A list of child nodes.
        """
        return [self.internal_nodes[edge.tail] for edge in node.relations["out"]]

    def get_parent(self, node: Node) -> Optional[Node]:
        """Get the parent of a given node in the tree.

        Args:
            node (Node): The node to get the parent for.

        Returns:
            Optional[Node]: The parent node, or None if the node is the root.
        """
        parent_edges = list(node.relations["in"])
        return self.internal_nodes[parent_edges[0].head] if parent_edges else None

    def is_leaf(self, node: Node) -> bool:
        """Check if a node is a leaf node (has no children).

        Args:
            node (Node): The node to check.

        Returns:
            bool: True if the node is a leaf, False otherwise.
        """
        return len(node.relations["out"]) == 0

    def get_leaves(self) -> List[Node]:
        """Get all leaf nodes in the tree.

        Returns:
            List[Node]: A list of all leaf nodes in the tree.
        """
        return [node for node in self.internal_nodes if self.is_leaf(node)]

    def depth(self, node: Node) -> int:
        """Calculate the depth of a node in the tree.

        Args:
            node (Node): The node to calculate the depth for.

        Returns:
            int: The depth of the node (0 for root, 1 for root's children, etc.)
        """
        depth = 0
        current = node
        while self.get_parent(current):
            depth += 1
            current = self.get_parent(current)
        return depth

    def height(self) -> int:
        """Calculate the height of the tree.

        Returns:
            int: The height of the tree (longest path from root to a leaf).
        """
        if not self.root:
            return 0

        def dfs_height(node: Node) -> int:
            if self.is_leaf(node):
                return 0
            return 1 + max(dfs_height(child) for child in self.get_children(node))

        return dfs_height(self.root)


# Path: lion_core/generic/graph.py
