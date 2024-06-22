"""
This module defines the Node class, representing a node in a graph-like
structure within LionAGI. Nodes can form relationships with other nodes
through directed edges, enabling construction and manipulation of complex
relational networks.

Includes functionality for managing relationships, such as adding,
modifying, and removing edges, and querying related nodes and connections.
"""

from pydantic import Field
from pandas import Series

from lionagi.os.lib import to_list
from ..abc import (
    Component,
    Condition,
    Relatable,
    RelationError,
    get_lion_id,
)
from ..pile.pile import pile, Pile
from ..edge.edge import Edge


class Node(Component, Relatable):
    """
    Node in a graph structure, can connect to other nodes via edges.

    Extends `Component` by incorporating relational capabilities, allowing
    nodes to connect through 'in' and 'out' directed edges, representing
    incoming and outgoing relationships.

    Attributes:
        relations (dict[str, Pile]): Dictionary holding 'Pile' instances
            for incoming ('in') and outgoing ('out') edges.
    """

    relations: dict[str, Pile] = Field(
        default_factory=lambda: {"in": pile(), "out": pile()},
        description="The relations of the node.",
    )

    @property
    def edges(self) -> Pile[Edge]:
        """
        Get unified view of all incoming and outgoing edges.

        Returns:
            Combined pile of all edges connected to this node.
        """
        return self.relations["in"] + self.relations["out"]

    @property
    def related_nodes(self) -> list[str]:
        """
        Get list of all unique node IDs directly related to this node.

        Returns:
            List of node IDs related to this node.
        """
        all_nodes = set(to_list([[i.head, i.tail] for i in self.edges]))
        all_nodes.discard(self.ln_id)
        return list(all_nodes)

    @property
    def node_relations(self) -> dict:
        """
        Get categorized view of direct relationships into groups.

        Returns:
            Dict with keys 'in' and 'out', each containing a mapping of
            related node IDs to lists of edges representing relationships.
        """
        out_node_edges = {}
        if not self.relations["out"].is_empty():
            for edge in self.relations["out"]:
                for node_id in self.related_nodes:
                    if edge.tail == node_id:
                        out_node_edges.setdefault(node_id, []).append(edge)

        in_node_edges = {}
        if not self.relations["in"].is_empty():
            for edge in self.relations["in"]:
                for node_id in self.related_nodes:
                    if edge.head == node_id:
                        in_node_edges.setdefault(node_id, []).append(edge)

        return {"out": out_node_edges, "in": in_node_edges}

    @property
    def predecessors(self) -> list[str]:
        """
        Get list of IDs of nodes with direct incoming relation to this.

        Returns:
            List of node IDs that precede this node.
        """
        return [
            node_id for node_id, edges in self.node_relations["in"].items() if edges
        ]

    @property
    def successors(self) -> list[str]:
        """
        Get list of IDs of nodes with direct outgoing relation from this.

        Returns:
            List of node IDs that succeed this node.
        """
        return [
            node_id for node_id, edges in self.node_relations["out"].items() if edges
        ]

    def relate(
        self,
        node: "Node",
        direction: str = "out",
        condition: Condition | None = None,
        label: str | None = None,
        bundle: bool = False,
    ) -> None:
        """
        Establish directed relationship from this node to another.

        Args:
            node: Target node to relate to.
            direction: Direction of edge ('in' or 'out'). Default 'out'.
            condition: Optional condition to associate with edge.
            label: Optional label for edge.
            bundle: Whether to bundle edge with others. Default False.

        Raises:
            ValueError: If direction is neither 'in' nor 'out'.
        """
        if direction not in ["in", "out"]:
            raise ValueError(
                f"Invalid value for direction: {direction}, " "must be 'in' or 'out'"
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

    def remove_edge(self, node: "Node", edge: Edge | str) -> bool:
        """
        Remove specified edge or all edges between this and another node.

        Args:
            node: Other node involved in edge.
            edge: Specific edge to remove or 'all' to remove all edges.

        Returns:
            True if edge(s) successfully removed, False otherwise.

        Raises:
            RelationError: If removal fails or edge does not exist.
        """
        edge_piles = [
            self.relations["in"],
            self.relations["out"],
            node.relations["in"],
            node.relations["out"],
        ]

        if not all(pile.exclude(edge) for pile in edge_piles):
            raise RelationError(f"Failed to remove edge between nodes.")
        return True

    def unrelate(self, node: "Node", edge: Edge | str = "all") -> bool:
        """
        Remove all or specific relationships between this and another node.

        Args:
            node: Other node to unrelate from.
            edge: Specific edge to remove or 'all' for all. Default 'all'.

        Returns:
            True if relationships successfully removed, False otherwise.

        Raises:
            RelationError: If operation fails to unrelate nodes.
        """
        if edge == "all":
            edges = self.node_relations["out"].get(
                node.ln_id, []
            ) + self.node_relations["in"].get(node.ln_id, [])
        else:
            edges = [get_lion_id(edge)]

        if not edges:
            raise RelationError(f"Node is not related to {node.ln_id}.")

        try:
            for edge_id in edges:
                self.remove_edge(node, edge_id)
            return True
        except RelationError as e:
            raise e

    def __str__(self):
        _dict = self.to_dict()
        _dict["relations"] = [
            len(self.relations["in"]),
            len(self.relations["out"]),
        ]
        return Series(_dict).__str__()

    def __repr__(self):
        return self.__str__()


from enum import Enum
from pydantic import Field
from ..abc import Condition
from ..util import to_list_type
from ..generic.node import Node


class TreeLabel(str, Enum):
    """Enumeration representing tree relationships."""

    PARENT = "parent"
    CHILD = "child"


class TreeNode(Node):
    """Represents a node in a tree structure."""

    parent: Node | None = Field(
        default=None,
        description="The parent node, as an instance of Node.",
    )

    @property
    def children(self) -> list[str]:
        """Return a list of child node ids."""
        if not self.parent:
            return list(self.related_nodes)
        else:
            return [node for node in self.related_nodes if node != self.parent.ln_id]

    def relate_child(
        self,
        node: Node | list[Node],
        condition: Condition | None = None,
        bundle: bool = False,
    ) -> None:
        """Establish a parent-child relationship with the given node(s)."""
        children = to_list_type(node)
        for _child in children:
            self.relate(
                _child,
                direction="out",
                # label=TreeLabel.PARENT,
                condition=condition,
                bundle=bundle,
            )
            if isinstance(_child, TreeNode):
                _child.parent = self

    def relate_parent(
        self,
        node: Node,
        condition: Condition | None = None,
        bundle: bool = False,
    ) -> None:
        """Establish a parent-child relationship with the given parent node."""
        if self.parent:
            self.unrelate(self.parent)
        self.relate(
            node,
            direction="in",
            # label=TreeLabel.PARENT,
            condition=condition,
            bundle=bundle,
        )
        self.parent = node

    def unrelate_parent(self):
        """Remove the parent-child relationship with the parent node."""
        self.unrelate(self.parent)
        self.parent = None

    def unrelate_child(self, child: Node | list[Node]):
        """Remove the parent-child relationship with the given child node(s)."""
        children: list[Node] = [child] if isinstance(child, Node) else child
        for _child in children:
            self.unrelate(_child)
            if isinstance(_child, TreeNode):
                _child.parent = None
