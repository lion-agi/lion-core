"""BaseGraph module for the Lion framework."""

from collections.abc import Sequence
from lion_core.generic.node import Node
from lion_core.generic.edge import Edge
from lion_core.generic.hyper_edge import HyperEdge
from lion_core.abc.concept import AbstractCondition, Actionable
from lion_core.util.sys_util import SysUtil
from lion_core.exceptions import LionTypeError, ItemNotFoundError
from .relation_manager import RelationManager


class BaseGraph(Node):
    """
    Represents a base graph structure with nodes and edges.

    Supports various edge types including directed/undirected and
    weighted/unweighted edges and hyperedges.

    Attributes:
        nodes (dict[str, Node]): Dictionary of nodes in the graph.
        edges (dict[str, Edge | HyperEdge]): Dictionary of edges in the graph.
        relation_manager (RelationManager): Manages node-edge relationships.
    """

    def __init__(self, **kwargs):
        """Initialize the BaseGraph."""
        super().__init__(**kwargs)
        self.nodes: dict[str, Node] = {}
        self.edges: dict[str, Edge | HyperEdge] = {}
        self.relation_manager = RelationManager()

    def add_node(self, node: Node) -> None:
        """
        Add a node to the graph.

        Args:
            node: The node to add.
        """
        self.nodes[node.ln_id] = node

    def add_edge(
        self,
        nodes: Sequence[Node],
        condition: AbstractCondition | None = None,
        label: str | None = None,
        directed: bool = False,
        weighted: bool = False,
        **kwargs
    ) -> Edge | HyperEdge:
        """
        Add an edge or hyperedge between nodes in the graph.

        Args:
            nodes: List of nodes to connect.
            condition: Edge condition.
            label: Edge label.
            directed: Whether the edge is directed.
            weighted: Whether the edge is weighted.
            **kwargs: Additional edge attributes.

        Returns:
            The created edge.

        Raises:
            ValueError: If fewer than 2 nodes are provided.
        """
        if len(nodes) < 2:
            raise ValueError("An edge must connect at least two nodes.")

        node_ids = [node.ln_id for node in nodes]

        if len(nodes) == 2:
            edge = Edge(
                head=nodes[0], tail=nodes[1], condition=condition,
                label=label, directed=directed, weighted=weighted, **kwargs
            )
            node_dict = (
                {'head': {edge.head}, 'tail': {edge.tail}} if directed
                else {'nodes': set(node_ids)}
            )
        else:
            edge = HyperEdge(
                nodes=nodes, directed=directed, weighted=weighted,
                condition=condition, label=label, **kwargs
            )
            node_dict = edge.nodes if directed else {'nodes': set(node_ids)}

        self.edges[edge.ln_id] = edge
        for node in nodes:
            self.add_node(node)

        self.relation_manager.add_relation(edge.ln_id, node_dict)

        return edge

    def remove_edge(self, edge: Edge | HyperEdge | str) -> None:
        """
        Remove an edge from the graph.

        Args:
            edge: The edge to remove.

        Raises:
            ItemNotFoundError: If the edge doesn't exist in the graph.
        """
        edge_id = SysUtil.get_lion_id(edge)
        if edge_id not in self.edges:
            raise ItemNotFoundError(f"Edge {edge_id} does not exist in the graph.")

        self.relation_manager.remove_relation(edge_id)
        del self.edges[edge_id]

    def remove_node(self, node: Node | str) -> None:
        """
        Remove a node and all its associated edges from the graph.

        Args:
            node: The node to remove.

        Raises:
            ItemNotFoundError: If the node doesn't exist in the graph.
        """
        node_id = SysUtil.get_lion_id(node)
        if node_id not in self.nodes:
            raise ItemNotFoundError(f"Node {node_id} does not exist in the graph.")

        associated_edges = self.relation_manager.remove_node(node_id)
        for edge_id in associated_edges:
            del self.edges[edge_id]

        del self.nodes[node_id]

    def get_node_edges(
        self,
        node: Node | str,
        edge_type: type | None = None,
        label: str | Sequence[str] | None = None
    ) -> list[Edge | HyperEdge]:
        """
        Get the edges of a node, optionally filtered by type and label.

        Args:
            node: The node to get edges for.
            edge_type: Type of edges to return.
            label: Label(s) to filter by.

        Returns:
            List of edges connected to the node.

        Raises:
            ItemNotFoundError: If the node doesn't exist in the graph.
        """
        node_id = SysUtil.get_lion_id(node)
        if node_id not in self.nodes:
            raise ItemNotFoundError(f"Node {node_id} does not exist in the graph.")

        edge_ids = self.relation_manager.get_node_edges(node_id)
        edges = [self.edges[edge_id] for edge_id in edge_ids]

        if edge_type:
            edges = [edge for edge in edges if isinstance(edge, edge_type)]

        if label:
            labels = [label] if isinstance(label, str) else label
            edges = [edge for edge in edges if edge.label in labels]

        return edges

    def get_adjacent_nodes(self, node: Node | str) -> list[Node]:
        """
        Get all nodes adjacent to the given node.

        Args:
            node: The node to get adjacent nodes for.

        Returns:
            List of adjacent nodes.
        """
        node_id = SysUtil.get_lion_id(node)
        adjacent_node_ids = self.relation_manager.get_adjacent_nodes(node_id)
        return [self.nodes[adj_id] for adj_id in adjacent_node_ids]

    def get_heads(self) -> list[Node]:
        """
        Get all head nodes in the graph (nodes with no incoming edges).

        Returns:
            List of head nodes.
        """
        heads = []
        for node_id, node in self.nodes.items():
            is_head = True
            for edge_id in self.relation_manager.get_node_edges(node_id):
                edge = self.edges[edge_id]
                edge_nodes = self.relation_manager.get_edge_nodes(edge_id)
                if (isinstance(edge, Edge) and edge.directed and
                    node_id in edge_nodes['tail']):
                    is_head = False
                    break
                elif (isinstance(edge, HyperEdge) and edge.directed and
                      node_id in edge_nodes.get('tail', set())):
                    is_head = False
                    break
            if is_head and not isinstance(node, Actionable):
                heads.append(node)
        return heads

    def size(self) -> int:
        """
        Return the number of nodes in the graph.

        Returns:
            Number of nodes in the graph.
        """
        return len(self.nodes)

    def clear(self) -> None:
        """Clear all nodes and edges from the graph."""
        self.nodes.clear()
        self.edges.clear()
        self.relation_manager.clear()