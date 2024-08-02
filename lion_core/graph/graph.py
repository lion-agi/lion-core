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

from pydantic import Field, field_serializer

from lion_core.abc import Event, Relational
from lion_core.sys_util import SysUtil
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
    node_edge_mapping: Note = Field(
        default_factory=Note,
        description="The mapping for node and edges for search",
        exclude=True
    )

    @field_serializer("internal_nodes", "internal_edges")
    def _serialize_internal_piles(self, value):
        value = value.to_dict()
        value = value["pile_"]
        return value

    def add_node(self, node: Node) -> None:
        """
        Add a node to the graph.

        Args:
            node: The node to add.

        Raises:
            LionRelationError: If the node already exists in the graph.
        """
        try:
            if not isinstance(node, Node):
                raise LionRelationError("Failed to add node: Invalid node type.")
            _id = SysUtil.get_id(node)
            self.internal_nodes.insert(-1, node)
            self.node_edge_mapping.insert(_id, {"in": {}, "out": {}})
        except ItemExistsError as e:
            raise LionRelationError(f"Error adding node: {e}")

    def add_edge(self, edge: Edge) -> None:
        """
        Add a edge to the graph.

        Args:
            edge: The edge to add.

        Raises:
            LionRelationError: If the edge already exists in the graph.
        """
        try:
            if not isinstance(edge, Edge):
                raise LionRelationError("Failed to add edge: Invalid edge type.")
            if edge.head not in self.internal_nodes or edge.tail not in self.internal_nodes:
                raise LionRelationError("Failed to add edge: Either edge head or tail node does not exist in the graph.")
            self.internal_edges.insert(-1, edge)
            self.node_edge_mapping[edge.head, "out", edge.ln_id] = edge.tail
            self.node_edge_mapping[edge.tail, "in", edge.ln_id] = edge.head
        except ItemExistsError as e:
            raise LionRelationError(f"Error adding node: {e}")

    def remove_node(self, node: Node | str) -> None:
        _id = SysUtil.get_id(node)
        if _id not in self.internal_nodes:
            raise LionRelationError(f"Node {node} not found in the graph nodes.")

        in_edges = self.node_edge_mapping[_id, "in"]
        for edge_id, node_id in in_edges.items():
            self.node_edge_mapping[node_id, "out"].pop(edge_id)
            self.internal_edges.pop(edge_id)

        out_edges = self.node_edge_mapping[_id, "out"]
        for edge_id, node_id in out_edges.items():
            self.node_edge_mapping[node_id, "in"].pop(edge_id)
            self.internal_edges.pop(edge_id)

        self.node_edge_mapping.pop(_id)
        return self.internal_nodes.pop(_id)

    def remove_edge(self, edge: Edge | str) -> None:
        """Remove an edge from the graph."""
        _id = SysUtil.get_id(edge)
        if _id not in self.internal_edges:
            raise LionRelationError(f"Edge {edge} not found in the graph edges.")

        edge = self.internal_edges[_id]
        self.node_edge_mapping[edge.head, "out"].pop(_id)
        self.node_edge_mapping[edge.tail, "in"].pop(_id)
        return self.internal_edges.pop(_id)

    def find_node_edge(
        self,
        node: Any,
        direction: Literal["both", "in", "out"] = "both",
    ) -> Pile[Edge]:
        """

        Find edges connected to a node in a specific direction.

        Args:
            node: The node to find edges for.
            direction: The direction to search ("in" or "out").
                    it's from the node's perspective.

        Returns:
            A Pile of Edges connected to the node in the specified direction.
        """

        _id = SysUtil.get_id(node)
        if _id not in self.internal_nodes:
            raise LionRelationError(f"Node {node} not found in the graph nodes.")

        result = []

        if direction in {"in", "both"}:
            for edge_id in self.node_edge_mapping[_id, "in"].keys():
                result.append(self.internal_edges[edge_id])

        if direction in {"out", "both"}:
            for edge_id in self.node_edge_mapping[_id, "out"].keys():
                result.append(self.internal_edges[edge_id])

        return Pile(items=result, item_type={Edge})

    def get_heads(self) -> Pile:
        """
        Get all head nodes in the graph.

        Returns:
            Pile: A Pile containing all head nodes.
        """

        result = []
        for node_id in self.node_edge_mapping.keys():
            if self.node_edge_mapping[node_id, "in"] == {}:
                result.append(self.internal_nodes[node_id])

        return Pile(items=result, item_type={Node})

    def get_predecessors(self, node: Node):
        edges = self.find_node_edge(node, direction="in")
        result = []
        for edge in edges:
            node_id = edge.head
            result.append(self.internal_nodes[node_id])
        return Pile(items=result, item_type={Node})

    def get_successor(self, node: Node):
        edges = self.find_node_edge(node, direction="out")
        result = []
        for edge in edges:
            node_id = edge.tail
            result.append(self.internal_nodes[node_id])
        return Pile(items=result, item_type={Node})

# File: lion_core/graph/graph.py
