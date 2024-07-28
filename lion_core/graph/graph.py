"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing import Any, Literal

from pydantic import Field

from lion_core.abc import Event, Relational
from lion_core.sys_utils import SysUtil
from lion_core.generic import Pile, pile, Note
from lion_core.exceptions import LionRelationError, ItemExistsError, ItemNotFoundError
from lion_core.graph.edge_condition import EdgeCondition
from lion_core.graph.edge import Edge
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
        default_factory=lambda: pile({}, {Edge}),
        description="The internal edges of the graph.",
    )

    def add_node(self, node: Node) -> None:
        """
        Add a node to the graph.

        Args:
            node: The node to add.

        Raises:
            LionRelationError: If the node already exists in the graph.
        """
        try:
            self.internal_nodes.insert(-1, node)
            return
        except ItemExistsError as e:
            raise LionRelationError(f"Error adding node: {e}")

    def add_edge(
        self,
        head: Relational | str,
        tail: Relational | str,
        condition: EdgeCondition | None = None,
        labels: list[str] | None = None,
    ):
        try:
            for i in [head, tail]:
                if i not in self and not isinstance(i, Relational):
                    raise LionRelationError(f"Node {i} not found in the graph.")

            # if head and tail are not in self.internal_nodes:
            # they are relational objects now after the above check
            edge = Edge(head=head, tail=tail, condition=condition, labels=labels)
            self.internal_nodes.include([head, tail])
            self.internal_edges.include(edge)

        except Exception as e:
            raise LionRelationError(f"Error adding edge: ") from e

    def remove_node(
        self,
        node: Node | str,
        delete: bool = False,
    ) -> None:

        _id = SysUtil.get_id(node)
        if _id not in self.internal_nodes:
            raise LionRelationError(f"Node {node} not found in the graph.")

        to_remove = []
        for edge in self.internal_edges:
            if _id in [edge.head, edge.tail]:
                to_remove.append(edge.ln_id)

        edges = self.internal_edges.pop(to_remove)
        node = self.internal_nodes.pop(_id)

        if delete:
            del edges
            del node

    def remove_edge(self, edge: Edge | str, delete=False) -> None:
        """Remove an edge from the graph."""
        try:
            edge = self.internal_edges.pop(SysUtil.get_id(edge))
        except ItemNotFoundError as e:
            raise LionRelationError(f"Error removing edge: {e}")
        if delete:
            del edge

    def find_node_edge(
        self,
        node: Any,
        direction: Literal["both", "head", "tail"] = "both",
    ) -> dict[str : Pile[Edge]]:
        """
        Find edges connected to a node in a specific direction.

        Args:
            node: The node to find edges for.
            direction: The direction to search ("head" or "tail").
                    it's from the node's perspective.

        Returns:
            A Pile of Edges connected to the node in the specified direction.
        """

        out = Note()
        for edge in self.internal_edges:
            if direction in {"both", "head"} and edge.tail == SysUtil.get_id(node):
                idx = len(out.get("head", []))
                out.set(["head", idx], edge)

            if direction in {"both", "tail"} and edge.head == SysUtil.get_id(node):
                idx = len(out.get("tail", []))
                out.set(["tail", idx], edge)

        out["head"] = pile(out.get("head", []), item_type=Edge)
        out["tail"] = pile(out.get("tail", []), item_type=Edge)

        for i in ["head", "tail"]:
            if not out.get(i):
                out.pop(i)

        return {k: pile(v, item_type=Edge) for k, v in out.items()}

    def get_heads(self) -> Pile:
        """
        Get all head nodes in the graph.

        Returns:
            Pile: A Pile containing all head nodes.
        """

        def is_head(node: Node) -> bool:
            if isinstance(node, Event):
                return False
            if "head" in self.find_node_edge(node):
                return False
            return True

        return pile([node for node in self.internal_nodes if is_head(node)])


# File: lion_core/graph/graph.py
